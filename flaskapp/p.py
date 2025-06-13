# crawler.py
import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta
import concurrent.futures
import time
import random

# 配置
START_ID = 861573
END_ID = 960020
INITIAL_DATE = datetime(2017, 5, 11)
MAX_DATE_SHIFT = 7
BATCH_SIZE = 50
MAX_WORKERS = 5


# 如果 songs_meta.json 不存在，先创建一个空的 JSON 数组
if not os.path.exists("songs_meta.json"):
    with open("songs_meta.json", "w", encoding="utf-8") as f:
        f.write("[]")

# 如果 failed_songs.txt 不存在，就创建一个空文件
if not os.path.exists("failed_songs.txt"):
    open("failed_songs.txt", "a", encoding="utf-8").close()

SONGS_JSON = "songs_meta.json"
FAILED_FILE = "failed_songs.txt"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

session = requests.Session()
session.headers.update(HEADERS)

def load_songs():
    if os.path.exists(SONGS_JSON):
        with open(SONGS_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_songs(songs):
    with open(SONGS_JSON, "w", encoding="utf-8") as f:
        json.dump(songs, f, ensure_ascii=False, indent=2)

def log_failed(song_id):
    with open(FAILED_FILE, "a", encoding="utf-8") as f:
        f.write(f"{song_id}\n")

def find_mp3_url(song_id, base_date):
    base = "https://music.jsbaidu.com/upload/128"
    dates = [base_date + timedelta(days=i) for i in range(MAX_DATE_SHIFT)]
    for d in dates:
        url = f"{base}/{d:%Y/%m/%d}/{song_id}.mp3"
        try:
            r = session.head(url, timeout=3)
            if r.status_code == 200:
                print(f"🎯 MP3 URL: {url}")
                return url
        except:
            pass
    return None

def get_song_info(song_id):
    url = f"https://www.9ku.com/play/{song_id}.htm"
    res = session.get(url, timeout=10)
    if res.status_code != 200:
        return None

    soup = BeautifulSoup(res.text, "html.parser")
    title = soup.find("h1").text.strip() if soup.find("h1") else f"未知歌曲_{song_id}"
    artist = soup.find("h2").text.strip() if soup.find("h2") else "未知歌手"

    info = {
        "song_id": song_id,
        "title": title,
        "artist": artist,
        "play_url": f"/play/{song_id}"
    }

    # 专辑 & 发行时间
    div = soup.find("div", class_="songText")
    if div:
        for p in div.find_all("p", class_="p1"):
            t = p.get_text()
            if "发行时间：" in t:
                info["release_date"] = t.split("发行时间：")[1].split("&")[0].strip()
            if "所属专辑：" in t:
                info["album"] = p.find("a").text.strip() if p.find("a") else None

    # 歌词 URL
    lyric = soup.find("textarea", id="lrc_content")
    if lyric and lyric.text.strip():
        info["has_lyric"] = True
        info["lyric_url"] = f"/lyric/{song_id}"
    else:
        info["has_lyric"] = False

    # MP3 URL（基于初始日期尝试）
    mp3_url = find_mp3_url(song_id, INITIAL_DATE)
    if mp3_url:
        info["mp3_url"] = mp3_url
    else:
        info["mp3_url"] = None

    return info

def crawl_songs():
    songs = load_songs()
    existing = {s["song_id"] for s in songs}

    for song_id in range(START_ID, END_ID + 1):
        if song_id in existing:
            continue

        info = get_song_info(song_id)
        if info:
            songs.append(info)
            print(f"✅ 爬取成功: {info['title']} (ID:{song_id})")
        else:
            log_failed(song_id)
            print(f"❌ 爬取失败: ID {song_id}")

        if len(songs) % BATCH_SIZE == 0:
            save_songs(songs)
            # 随机短暂休眠，防止被封
            time.sleep(random.uniform(0.5, 1.5))

    save_songs(songs)
    print("🎉 爬取完成，已保存到", SONGS_JSON)

if __name__ == "__main__":
    crawl_songs()
