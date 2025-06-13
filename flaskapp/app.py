# app.py
from flask import Flask, jsonify, request, render_template, abort, make_response,send_file
import requests
import json
import os

app = Flask(__name__)

# 配置
SONGS_JSON = "songs_meta.json"
CACHE_DIR = "temp_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def load_songs():
    with open(SONGS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/songs')
def get_songs():
    query = request.args.get('q', '').lower()
    songs = load_songs()
    if query:
        songs = [s for s in songs if query in s['title'].lower() or query in s['artist'].lower()]
    return jsonify({'songs': songs})

@app.route('/play/<int:song_id>')
def play_song(song_id):
    # 从 JSON 文件中查找歌曲
    songs = load_songs()
    song = next((s for s in songs if s["song_id"] == song_id), None)
    if not song or not song.get("mp3_url"):
        return "Not Found", 404

    mp3_url = song["mp3_url"]
    local_path = os.path.join("music", f"{song_id}.mp3")
    os.makedirs("music", exist_ok=True)

    # 如果本地没有，就下载
    if not os.path.exists(local_path):
        try:
            r = requests.get(mp3_url, timeout=10)
            if r.status_code == 200:
                with open(local_path, "wb") as f:
                    f.write(r.content)
            else:
                return "下载失败", 500
        except Exception as e:
            return f"请求出错: {e}", 500

    return send_file(local_path, mimetype="audio/mpeg")

@app.route('/lyric/<int:song_id>')
def get_lyric(song_id):
    songs = load_songs()
    song = next((s for s in songs if s['song_id'] == song_id), None)
    if not song or not song.get('has_lyric'):
        return ""
    # 直接从网页抓取最新歌词
    res = requests.get(f"https://www.9ku.com/play/{song_id}.htm", timeout=10)
    if res.status_code != 200:
        return ""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(res.text, "html.parser")
    ta = soup.find("textarea", id="lrc_content")
    return ta.text.strip() if ta else ""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
