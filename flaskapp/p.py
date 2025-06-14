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
START_ID = 1
END_ID = 1060020
INITIAL_DATE = datetime(2010, 3, 16)  # 默认初始日期
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

def brute_force_date(song_id, start_date, max_days=365 * 3):
    """暴力测试找到ID对应的合理日期"""
    base_url = "https://music.jsbaidu.com/upload/128"
    
    # 向前测试（日期递增，适用于更大的song_id）
    for i in range(max_days):
        test_date = start_date + timedelta(days=i)
        if test_date > datetime.now():
            continue
        url = f"{base_url}/{test_date:%Y/%m/%d}/{song_id}.mp3"
        try:
            r = session.head(url, timeout=2)
            if r.status_code == 200:
                print(f"🎯 暴力测试成功 (ID:{song_id} 日期:{test_date.date()})")
                return test_date
        except:
            continue
    
    # 向后测试（日期递减，适用于更小的song_id）
    for i in range(max_days):
        test_date = start_date - timedelta(days=i)
        url = f"{base_url}/{test_date:%Y/%m/%d}/{song_id}.mp3"
        try:
            r = session.head(url, timeout=2)
            if r.status_code == 200:
                print(f"🎯 暴力测试成功 (ID:{song_id} 日期:{test_date.date()})")
                return test_date
        except:
            continue
    
    print(f"⚠️ 暴力测试失败 (ID:{song_id}) 使用初始日期")
    return start_date

def load_progress():
    """加载进度，自动探测日期关系"""
    if os.path.exists(PROGRESS_JSON):
        try:
            with open(PROGRESS_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
            sid = int(data.get("song_id", START_ID))
            
            # 尝试加载保存的日期
            ldate_str = data.get("last_date")
            if ldate_str:
                try:
                    ldate = datetime.fromisoformat(ldate_str)
                    return sid, ldate
                except ValueError:
                    pass
        except Exception as e:
            print(f"⚠️ 进度文件错误: {e}，重新探测日期")
    
    # 如果没有进度文件或文件损坏，执行暴力测试探测日期
    print("🔍 无进度文件或文件损坏，自动探测起始日期")
    detected_date = brute_force_date(START_ID, INITIAL_DATE)
    return START_ID, detected_date

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
    """带重试机制的请求包装器"""
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
    """提取歌曲元数据"""
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
    """检查URL是否存在"""
    try:
        r = session.head(url, timeout=3)
        return url if r.status_code == 200 else None
    except:
        return None

def find_mp3_url(song_id, base_date):
    """寻找MP3文件URL"""
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
    """安全写入JSON文件"""
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
    """后台线程，负责写入元数据文件"""
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
    """处理单个歌曲ID"""
    # 当处理新ID时检查cur_date是否合理
    test_url = f"https://music.jsbaidu.com/upload/128/{cur_date:%Y/%m/%d}/{song_id}.mp3"
    r = session.head(test_url, timeout=2)
    if r.status_code != 200:
        print(f"⚠️ 日期校准 {cur_date.date()} 可能已过期，重新探测")
        cur_date = brute_force_date(song_id, cur_date)

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
        "title": info['title'],
        "artist": info['artist'],
        "release_date": info.get('release_date'),
        "album": info.get('album'),
        "has_lyric": info['has_lyric'],
        "lyric_url": info['lyric_url'],  # 保存歌词地址
        "mp3_url": mp3_url,
        "filename": filename,
    }
    # 放入写队列，由写线程异步写入文件
    meta_queue.put(meta_entry)
    print(f"📦 已放入写队列（ID:{song_id}）")

    return song_id, new_date

def process_batch(batch_ids, cur_date):
    """处理一批歌曲ID"""
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
    except KeyboardInterrupt:
        print("⛔ 用户中断，保存进度后退出")
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
