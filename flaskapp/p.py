import requests
from bs4 import BeautifulSoup, SoupStrainer
import json
import os
from datetime import datetime
from urllib.parse import quote

# 配置
SONGS_JSON = "songs_meta.json"
FAILED_FILE = "failed_songs.txt"
START_ID = 861573
END_ID = 960020
BATCH_SIZE = 50
MAX_WORKERS = 5

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

def get_song_info(song_id):
    try:
        url = f"https://www.9ku.com/play/{song_id}.htm"
        res = session.get(url, timeout=10)
        if res.status_code != 200:
            return None
        
        soup = BeautifulSoup(res.text, "html.parser")
        
        title = soup.find("h1").text.strip() if soup.find("h1") else f"未知歌曲_{song_id}"
        artist = soup.find("h2").text.strip() if soup.find("h2") else "未知歌手"
        
        # 获取其他信息
        info = {"song_id": song_id, "title": title, "artist": artist}
        
        # 尝试获取专辑和发行时间
        song_text = soup.find("div", class_="songText")
        if song_text:
            for p in song_text.find_all("p", class_="p1"):
                text = p.get_text()
                if "发行时间：" in text:
                    info["release_date"] = text.split("发行时间：")[1].split("&")[0].strip()
                if "所属专辑：" in text:
                    info["album"] = p.find("a").text.strip() if p.find("a") else None
        
        # 获取歌词URL
        lrc_textarea = soup.find("textarea", id="lrc_content")
        if lrc_textarea:
            info["has_lyric"] = bool(lrc_textarea.text.strip())
        
        # 构造播放URL (实际播放时再获取)
        info["play_url"] = f"/play/{song_id}"
        
        return info
    except Exception as e:
        print(f"获取歌曲{song_id}信息失败: {e}")
        return None

def crawl_songs():
    existing_songs = {s["song_id"] for s in load_songs()}
    songs = load_songs()
    
    for song_id in range(START_ID, END_ID + 1):
        if str(song_id) in existing_songs:
            continue
            
        info = get_song_info(song_id)
        if info:
            songs.append(info)
            print(f"获取成功: {info['title']} - {info['artist']} (ID: {song_id})")
        else:
            log_failed(song_id)
            print(f"获取失败: ID {song_id}")
            
        # 每获取一定数量保存一次
        if len(songs) % BATCH_SIZE == 0:
            save_songs(songs)
    
    save_songs(songs)

if __name__ == "__main__":
    crawl_songs()