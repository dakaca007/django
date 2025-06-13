from flask import Flask, jsonify, send_file, request, render_template
import os
from urllib.parse import unquote

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
MUSIC_DIR = os.path.join(BASE_DIR, 'downloaded_music')
LYRIC_DIR = os.path.join(BASE_DIR, 'lyrics')
os.makedirs(LYRIC_DIR, exist_ok=True)
os.makedirs(MUSIC_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lyrics/<path:filename>')
def lyric_file(filename):
    safe_filename = unquote(filename)
    base_name = os.path.splitext(safe_filename)[0]
    lrc_filename1 = base_name + '.lrc'
    lrc_filename2 = base_name + 'lrc'

    abs_path1 = os.path.abspath(os.path.join(LYRIC_DIR, lrc_filename1))
    abs_path2 = os.path.abspath(os.path.join(LYRIC_DIR, lrc_filename2))

    if not abs_path1.startswith(LYRIC_DIR) or not abs_path2.startswith(LYRIC_DIR):
        return "Access denied", 403

    if os.path.exists(abs_path1):
        with open(abs_path1, encoding='utf-8') as f:
            return f.read()
    elif os.path.exists(abs_path2):
        with open(abs_path2, encoding='utf-8') as f:
            return f.read()
    else:
        return ""

@app.route('/songs')
def songs_api():
    songs = []
    for filename in os.listdir(MUSIC_DIR):
        if filename.endswith('.mp3'):
            name_part = os.path.splitext(filename)[0]
            parts = name_part.split('_')
            song_name = parts[0] if len(parts) > 0 else name_part
            artist = parts[1] if len(parts) > 1 else '未知'
            songs.append({
                'name': song_name,
                'artist': artist,
                'filename': filename,
                'url': f'/music/{filename}'
            })
    return jsonify({'songs': songs})

@app.route('/music/<path:filename>')
def music_file(filename):
    safe_filename = unquote(filename)
    abs_path = os.path.abspath(os.path.join(MUSIC_DIR, safe_filename))
    if not abs_path.startswith(MUSIC_DIR):
        return "Access denied", 403
    if not os.path.exists(abs_path):
        return "File not found", 404
    return send_file(abs_path, mimetype='audio/mpeg')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
