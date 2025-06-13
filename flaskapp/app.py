from flask import Flask, jsonify, request, render_template, abort, make_response
import requests
from bs4 import BeautifulSoup
from io import BytesIO
import json
import os
from datetime import datetime
from urllib.parse import quote
from functools import lru_cache

app = Flask(__name__)

# 配置
SONGS_JSON = "songs_meta.json"
CACHE_DIR = "temp_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# 加载歌曲元数据
def load_songs():
    if os.path.exists(SONGS_JSON):
        with open(SONGS_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# 获取MP3文件
def get_mp3_file(song_id):
    # 检查缓存
    cache_path = os.path.join(CACHE_DIR, f"{song_id}.mp3")
    if os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            return f.read()
    
    # 尝试多个可能的URL模式
    base_urls = [
        f"https://music.jsbaidu.com/upload/128/{datetime.now().strftime('%Y/%m/%d')}/{song_id}.mp3",
        f"https://mp3.9ku.com/m4a/{song_id}.m4a",
        f"https://mp3.9ku.com/hot/2004/{song_id}.mp3",
    ]
    
    for url in base_urls:
        try:
            res = requests.get(url, stream=True, timeout=10)
            if res.status_code == 200:
                # 缓存文件
                content = res.content
                with open(cache_path, "wb") as f:
                    f.write(content)
                return content
        except:
            continue
    
    return None

# 获取歌词
def get_lyric(song_id):
    try:
        url = f"https://www.9ku.com/play/{song_id}.htm"
        res = requests.get(url, timeout=10)
        if res.status_code != 200:
            return None
        
        soup = BeautifulSoup(res.text, "html.parser")
        lrc_textarea = soup.find("textarea", id="lrc_content")
        return lrc_textarea.text.strip() if lrc_textarea else None
    except:
        return None

# 路由
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/songs')
def get_songs():
    query = request.args.get('q', '').lower()
    songs = load_songs()
    
    if query:
        filtered = [
            s for s in songs 
            if query in s['title'].lower() or query in s['artist'].lower()
        ]
    else:
        filtered = songs
    
    return jsonify({
        'songs': [
            {
                'id': s['song_id'],
                'title': s['title'],
                'artist': s['artist'],
                'album': s.get('album', ''),
                'release_date': s.get('release_date', ''),
                'url': f"/play/{s['song_id']}"
            }
            for s in filtered
        ]
    })

@app.route('/play/<int:song_id>')
def play_song(song_id):
    mp3_data = get_mp3_file(song_id)
    if not mp3_data:
        abort(404)
    
    response = make_response(mp3_data)
    response.headers['Content-Type'] = 'audio/mpeg'
    response.headers['Content-Disposition'] = f'inline; filename="{song_id}.mp3"'
    return response

@app.route('/lyric/<int:song_id>')
def get_lyric_api(song_id):
    lyric = get_lyric(song_id)
    return lyric if lyric else ""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)