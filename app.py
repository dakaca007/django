# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, render_template, Response
import requests
import subprocess
import json
import os

app = Flask(__name__)

# 从配置文件中settings加载配置
app.config.from_pyfile('settings.py')
@app.route('/admin')
def editor():
    return render_template('editor.html')

@app.route('/open', methods=['POST'])
def open_file():
    file_path = request.form['file_path']
    if os.path.exists(file_path):
        os.chdir(file_path)  # 更改当前工作目录
        with open(file_path, 'r') as file:
            content = file.read()
        return render_template('editor.html', content=content)
    else:
        return '文件不存在'


@app.route('/save', methods=['POST'])
def save_file():
    content = request.form['content']
    file_path = request.form['file_path']

    with open(file_path, 'w') as file:
        file.write(content)

    return '文件已保存'

@app.route('/delete', methods=['POST'])
def delete_file():
    file_path = request.form['file_path']
    if os.path.exists(file_path):
        os.remove(file_path)
        return '文件已删除'
    else:
        return '文件不存在'
        
@app.route("/chat", methods=["GET"])
def index():
    return render_template("chat.html")
@app.route("/m", methods=["GET"])
def indexm():
    return render_template("index.html")
@app.route('/cm')
def indexcm():
    return render_template('indexcm.html')
@app.route('/')
def indexcmtest():
    response = requests.get('http://localhost:8080/')
    return response.text
@app.route('/execute', methods=['POST'])
def execute():
    directory = request.form['directory']
    try:
        os.chdir(directory)  # 改变工作目录为表单字段的值
        command = request.form['command']
        result = subprocess.check_output(command, shell=True)
        result = result.decode('utf-8')  # 将字节流转换为字符串
        return render_template('indexcm.html', result=result)
    except Exception as e:
        error_message = str(e)
        return render_template('indexcm.html', error_message=error_message)
@app.route("/chat", methods=["POST"])
def chat():
    messages = request.form.get("prompts", None)
    apiKey = request.form.get("apiKey", None)
    model = request.form.get("model", "gpt-3.5-turbo-16k")
    if messages is None:
        return jsonify({"error": {"message": "请输入prompts！", "type": "invalid_request_error", "code": ""}})

    if apiKey is None:
        apiKey = app.config['OPENAI_API_KEY']

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {apiKey}",
    }

    # json串转对象
    prompts = json.loads(messages)

    data = {
        "messages": prompts,
        "model": "gpt-3.5-turbo-16k",
        "max_tokens": 1024,
        "temperature": 0.5,
        "top_p": 1,
        "n": 1,
        "stream": True,
    }

    try:
        resp = requests.post(
            url=app.config["URL"],
            headers=headers,
            json=data,
            stream=True,
            timeout=(10, 10)  # 连接超时时间为10秒，读取超时时间为10秒
        )
    except requests.exceptions.Timeout:
        return jsonify({"error": {"message": "请求超时，请稍后再试！", "type": "timeout_error", "code": ""}})

    # 迭代器实现流式响应
    def generate():
        errorStr = ""
        for chunk in resp.iter_lines():
            if chunk:
                streamStr = chunk.decode("utf-8").replace("data: ", "")
                try:
                    streamDict = json.loads(streamStr)  # 说明出现返回信息不是正常数据,是接口返回的具体错误信息
                except:
                    errorStr += streamStr.strip()  # 错误流式数据累加
                    continue
                delData = streamDict["choices"][0]
                if delData["finish_reason"] != None :
                    break
                else:
                    if "content" in delData["delta"]:
                        respStr = delData["delta"]["content"]
                        # print(respStr)
                        yield respStr

        # 如果出现错误，此时错误信息迭代器已处理完，app_context已经出栈，要返回错误信息，需要将app_context手动入栈
        if errorStr != "":
            with app.app_context():
                yield errorStr

    return Response(generate(), content_type='application/octet-stream')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
