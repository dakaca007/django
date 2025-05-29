from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room
import subprocess
import os
import uuid
from threading import Lock

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET')
socketio = SocketIO(app, cors_allowed_origins="*")

# 配置
CODE_DIR = "/tmp/code"
os.makedirs(CODE_DIR, exist_ok=True)

# 运行时状态
processes = {}
process_lock = Lock()
file_system = {}
user_history = {}

@app.route('/')
def index():
    return render_template('index.html')

# 代码执行端点
@app.route('/execute', methods=['POST'])
def execute_code():
    data = request.json
    code = data.get('code')
    language = data.get('language', 'python')
    
    try:
        # 配置执行环境
        config = {
            'python': {'ext': 'py', 'cmd': ['python3', '{filename}']},
            'javascript': {'ext': 'js', 'cmd': ['node', '{filename}']},
            'shell': {'ext': 'sh', 'cmd': ['bash', '{filename}']}
        }.get(language, 'python')

        # 写入临时文件
        filename = f"{CODE_DIR}/temp.{config['ext']}"
        with open(filename, 'w') as f:
            f.write(code)
        
        # 执行代码
        cmd = [c.replace('{filename}', filename) for c in config['cmd']]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        return jsonify({
            "output": result.stdout,
            "error": result.stderr,
            "returncode": result.returncode
        })
    except subprocess.TimeoutExpired:
        return jsonify({"error": "执行超时"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# WebSocket 实时功能
@socketio.on('connect')
def handle_connect():
    print(f"客户端连接: {request.sid}")

@socketio.on('code_update')
def handle_code_update(data):
    emit('code_update', data, broadcast=True, include_self=False)

@socketio.on('cursor_update')
def handle_cursor_update(data):
    emit('cursor_update', {
        'id': request.sid,
        'pos': data['pos']
    }, broadcast=True, include_self=False)

@socketio.on('execute')
def handle_execute(data):
    sid = request.sid
    code = data['code']
    language = data['language']
    
    # 生成唯一执行ID
    exec_id = str(uuid.uuid4())
    join_room(exec_id, sid)

    # 配置语言环境
    config = {
        'python': {'ext': 'py', 'cmd': ['python3', '{filename}']},
        'javascript': {'ext': 'js', 'cmd': ['node', '{filename}']},
        'shell': {'ext': 'sh', 'cmd': ['bash', '{filename}']}
    }.get(language, 'python')

    # 写入临时文件
    filename = f"{CODE_DIR}/{exec_id}.{config['ext']}"
    with open(filename, 'w') as f:
        f.write(code)

    # 启动进程
    cmd = [c.replace('{filename}', filename) for c in config['cmd']]
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True
    )

    # 存储进程引用
    with process_lock:
        processes[exec_id] = proc

    # 记录执行历史
    if sid not in user_history:
        user_history[sid] = []
    user_history[sid].append({
        'code': code,
        'language': language,
        'timestamp': datetime.now().isoformat()
    })

    # 实时输出处理线程
    def stream_output():
        while proc.poll() is None:
            line = proc.stdout.readline()
            if line:
                emit('output', {'type': 'stdout', 'data': line}, room=exec_id)
        
        # 处理剩余输出
        for line in proc.stdout:
            if line.strip():
                emit('output', {'type': 'stdout', 'data': line}, room=exec_id)
        for line in proc.stderr:
            if line.strip():
                emit('output', {'type': 'stderr', 'data': line}, room=exec_id)
        
        emit('exec_end', {'code': proc.returncode}, room=exec_id)
        with process_lock:
            del processes[exec_id]

    socketio.start_background_task(stream_output)

@socketio.on('stop_execution')
def handle_stop(data):
    exec_id = data['exec_id']
    with process_lock:
        proc = processes.get(exec_id)
        if proc:
            proc.terminate()
            emit('output', {'type': 'stderr', 'data': '进程已终止'}, room=exec_id)

@socketio.on('file_op')
def handle_file_operation(data):
    sid = request.sid
    op = data['op']
    path = data.get('path')
    content = data.get('content')
    
    if op == 'list':
        emit('file_list', {'tree': file_system.get(sid, {})})
    elif op == 'save':
        if sid not in file_system:
            file_system[sid] = {}
        file_system[sid][path] = content
    elif op == 'delete':
        if sid in file_system and path in file_system[sid]:
            del file_system[sid][path]

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=80, debug=True)
