from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime
import time
import os
from werkzeug.utils import secure_filename
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB
socketio = SocketIO(app, cors_allowed_origins="*")
# 创建上传目录
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
# 存储用户和消息
users = {}
messages = []
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
# 添加文件上传路由
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return {'error': 'No file part'}, 400
    
    file = request.files['file']
    if file.filename == '':
        return {'error': 'No selected file'}, 400
    
    if file and allowed_file(file.filename):
        # 生成唯一文件名
        filename = secure_filename(file.filename)
        unique_name = f"{int(time.time())}_{filename}"
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
        file.save(save_path)
        return {'url': f"https://bm-p8ho.onrender.com/flask/static/uploads/{unique_name}"}
    
    return {'error': 'File type not allowed'}, 400
@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    emit('server_response', {'type': 'connect', 'data': '请先设置您的昵称'})

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in users:
        user_info = users.pop(request.sid)
        emit('server_response', {
            'type': 'notification',
            'data': f"{user_info['nickname']} 离开了聊天室",
            'timestamp': time.time()
        }, broadcast=True)

@socketio.on('set_nickname')
def handle_set_nickname(data):
    nickname = data['nickname'].strip()
    if not nickname:
        emit('server_response', {'type': 'error', 'data': '昵称不能为空'})
        return
        
    users[request.sid] = {
        'nickname': nickname,
        'joined_at': datetime.now().isoformat()
    }
    
    # 发送历史消息
    for msg in messages[-20:]:
        emit('server_response', msg)
    
    emit('server_response', {
        'type': 'notification',
        'data': f"欢迎 {nickname} 加入聊天室!",
        'timestamp': time.time()
    }, broadcast=True)
    
    emit('server_response', {
        'type': 'system',
        'data': '您已成功加入聊天室',
        'timestamp': time.time()
    })

@socketio.on('client_message')
def handle_client_message(data):
    if request.sid not in users:
        emit('server_response', {'type': 'error', 'data': '请先设置昵称'})
        return
        
    message = {
        'type': data.get('type', 'message'),  # 添加消息类型
        'nickname': users[request.sid]['nickname'],
        'content': data['content'],
        'timestamp': time.time()
    }
    
    messages.append(message)
    if len(messages) > 100:
        messages.pop(0)
    
    emit('server_response', message, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000, debug=True)