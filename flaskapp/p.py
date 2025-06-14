
import requests
from datetime import datetime, timedelta
import os
import time
import json
import random
from bs4 import BeautifulSoup, SoupStrainer
import concurrent.futures
from functools import lru_cache
import threading
import queue
import tempfile
import shutil

# 配置项
START_ID = 860000
END_ID = 1060020
INITIAL_DATE = datetime(2017, 3, 16)
MAX_DATE_SHIFT = 7
PROGRESS_JSON = "progress.json"
FAILED_FILE = "failed.txt"
SONGS_META_FILE = "songs_meta.json"
BATCH_SIZE = 20
MAX_WORKERS = 5
MAX_RETRIES = 3

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
session = requests.Session()
session.headers.update(HEADERS)

# 线程安全的队列，存放待写入的元数据
meta_queue = queue.Queue()

def load_progress():
    if os.path.exists(PROGRESS_JSON):
        try:
            with open(PROGRESS_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
            sid = int(data.get("song_id", START_ID))
            ldate = datetime.fromisoformat(data.get("last_date", INITIAL_DATE.isoformat()))
            return sid, ldate
        except Exception:
            print("⚠️ 进度文件损坏，重置进度")
    return START_ID, INITIAL_DATE

def save_progress(song_id, last_date):
    try:
        with open(PROGRESS_JSON, "w", encoding="utf-8") as f:
            json.dump({
                "song_id": song_id,
                "last_date": last_date.date().isoformat()
            }, f)
    except Exception as e:
        print(f"❌ 保存进度失败: {e}")

def log_failure(song_id):
    try:
        with open(FAILED_FILE, "a", encoding="utf-8") as f:
            f.write(f"{song_id}\n")
    except Exception as e:
        print(f"❌ 记录失败ID失败: {e}")

def sanitize_filename(name):
    return "".join(c for c in name if c.isalnum() or c in (" ", "_", "-")).strip()

def retry(func, *args, **kw):
    for i in range(MAX_RETRIES):
        try:
            return func(*args, **kw)
        except Exception as e:
            if i == MAX_RETRIES - 1:
                print(f"❌ 最终失败：{e}")
                return None
            wait = random.uniform(1, 2 ** i)
            print(f"🔁 重试 {i+1}/{MAX_RETRIES}，等待 {wait:.1f}s")
            time.sleep(wait)

@lru_cache(maxsize=2048)
def extract_song_info(song_id):
    def _():
        res = session.get(f"https://www.9ku.com/play/{song_id}.htm", timeout=5)
        if res.status_code != 200:
            return None
        strainer = SoupStrainer(["h1", "h2", "div", "textarea"])
        soup = BeautifulSoup(res.text, "html.parser", parse_only=strainer)
        title = soup.find("h1").text.strip() if soup.find("h1") else f"unknown_{song_id}"
        artist = soup.find("h2").text.strip() if soup.find("h2") else "unknown_artist"
        div = soup.find("div", class_="songText")
        release = album = None
        if div:
            for p in div.find_all("p", class_="p1"):
                t = p.get_text()
                if "发行时间：" in t: release = t.split("发行时间：")[1].split("&")[0].strip()
                if "所属专辑：" in t: album = p.find("a").text.strip() if p.find("a") else None
        lyric = soup.find("textarea", id="lrc_content")
        return {
            "song_id": song_id,
            "title": title,
            "artist": artist,
            "release_date": release,
            "album": album,
            "has_lyric": bool(lyric),
            "lyric_url": f"https://www.9ku.com/lyric/{song_id}.htm",  # 新增歌词页面地址
        }
    return retry(_)

def url_exists(url):
    try:
        r = session.head(url, timeout=3)
        return url if r.status_code == 200 else None
    except:
        return None

def find_mp3_url(song_id, base_date):
    base = "https://music.jsbaidu.com/upload/128"
    dates = [base_date + timedelta(days=i) for i in range(MAX_DATE_SHIFT)]
    with concurrent.futures.ThreadPoolExecutor() as ex:
        futures = {
            ex.submit(url_exists, f"{base}/{d:%Y/%m/%d}/{song_id}.mp3"): d
            for d in dates
        }
        for fut in concurrent.futures.as_completed(futures):
            url = fut.result()
            if url:
                print(f"🎯 找到 MP3（ID:{song_id} 日期:{futures[fut].date()}）")
                return url, futures[fut]
    print(f"🚫 未找到 MP3（ID:{song_id}）")
    return None, base_date

def safe_write_json(filename, data):
    tmpfd, tmpname = tempfile.mkstemp(suffix=".tmp", prefix="tmp_")
    try:
        with os.fdopen(tmpfd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        shutil.move(tmpname, filename)  # 原子替换
    except Exception:
        if os.path.exists(tmpname):
            os.remove(tmpname)
        raise

def meta_writer_thread(stop_event):
    all_meta = []
    if os.path.exists(SONGS_META_FILE):
        try:
            with open(SONGS_META_FILE, "r", encoding="utf-8") as f:
                all_meta = json.load(f)
        except Exception:
            print("⚠️ 无法读取原歌曲列表，写入新文件")

    while not stop_event.is_set() or not meta_queue.empty():
        try:
            meta = meta_queue.get(timeout=1)
            all_meta.append(meta)
            safe_write_json(SONGS_META_FILE, all_meta)
            meta_queue.task_done()
        except queue.Empty:
            continue
        except Exception as e:
            print(f"❌ 写入元数据时异常: {e}")

def process_one(song_id, cur_date):
    info = extract_song_info(song_id)
    if not info:
        log_failure(song_id)
        return song_id, None

    mp3_url, new_date = find_mp3_url(song_id, cur_date)
    if not mp3_url:
        log_failure(song_id)
        return song_id, None

    filename = sanitize_filename(f"{info['title']}_{info['artist']}_{song_id}.mp3")

    meta_entry = {
        "song_id": song_id,
        "title": info["title"],
        "artist": info["artist"],
        "release_date": info.get("release_date"),
        "album": info.get("album"),
        "has_lyric": info["has_lyric"],
        "lyric_url": info["lyric_url"],  # 保存歌词地址
        "mp3_url": mp3_url,
        "filename": filename,
    }
    # 放入写队列，由写线程异步写入文件
    meta_queue.put(meta_entry)
    print(f"📦 已放入写队列（ID:{song_id}）")

    return song_id, new_date

def process_batch(batch_ids, cur_date):
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = [ex.submit(process_one, sid, cur_date) for sid in batch_ids]
        for fut in concurrent.futures.as_completed(futures):
            sid, nd = fut.result()
            if nd:
                cur_date = nd
            # 这里不在每首歌保存进度，改成批量后再保存
    return cur_date

def main():
    sid, cdate = load_progress()
    print(f"🚀 开始采集，起始 ID: {sid}, 起始日期: {cdate.date()}")

    stop_event = threading.Event()
    writer = threading.Thread(target=meta_writer_thread, args=(stop_event,), daemon=True)
    writer.start()

    try:
        while sid < END_ID:
            end = min(sid + BATCH_SIZE, END_ID)
            print(f"\n🔄 批次采集 ID {sid}–{end - 1}")
            cdate = process_batch(range(sid, end), cdate)
            save_progress(end, cdate)  # 每批结束后保存进度
            sid = end
            dt = random.uniform(0.5, 1.5)
            print(f"⏳ 等待 {dt:.1f}s 继续")
            time.sleep(dt)
    except Exception as e:
        print(f"❌ 程序异常退出: {e}")
    finally:
        print("🛑 等待队列写完数据")
        meta_queue.join()
        stop_event.set()
        writer.join()

        print("🎉 所有采集任务完成")
        session.close()

if __name__ == "__main__":
    main()
