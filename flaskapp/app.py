from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import subprocess
import psutil
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET')
socketio = SocketIO(app, cors_allowed_origins="*")

# 代码执行沙箱配置
CODE_DIR = "/tmp/code"
os.makedirs(CODE_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/execute', methods=['POST'])
def execute_code():
    code = request.json.get('code')
    
    # 安全限制
    if len(code) > 10000:
        return jsonify({"error": "代码超过长度限制"}), 400
    
    try:
        # 写入临时文件
        with open(f"{CODE_DIR}/temp.py", "w") as f:
            f.write(code)
        
        # 在容器内安全执行
        result = subprocess.run(
            ['python3', f"{CODE_DIR}/temp.py"],
            capture_output=True,
            text=True,
            timeout=5,        # 执行超时限制
            check=True,
        )
        return jsonify({
            "output": result.stdout,
            "error": result.stderr
        })
    except subprocess.TimeoutExpired:
        return jsonify({"error": "执行超时"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 实时协作功能
@socketio.on('code_update')
def handle_code_update(data):
    # 广播代码更新
    emit('code_update', data, broadcast=True, include_self=False)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=80)
