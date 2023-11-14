# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, render_template, Response,redirect


from wtforms import Form, StringField, SubmitField
from wtforms.validators import DataRequired, Length
import requests
import subprocess
import json
import os
from werkzeug.utils import secure_filename
import sys
app = Flask(__name__, static_folder='static', static_url_path='/static')
 
def list_files(directory):
    file_list_html = '<ul>'
    for root, dirs, files in os.walk(directory):
        for file in files:
            # 构建文件链接
            file_path = os.path.relpath(os.path.join(root, file), directory)
             
            file_url = f"/static/{file_path}"
            edit_url = f"/edit/{file_path}"
            delete_url = f"/delete/{file_path}"
            rename_url = f"/rename/{file_path}"  # 添加重命名链接
            file_list_html += f'<li><a href="{file_url}">{file_path}</a> <a href="{edit_url}">编辑</a> <a href="{delete_url}">删除</a> <a href="{rename_url}">重命名</a></li>'
    file_list_html += '</ul>'
    return file_list_html   




@app.route('/new', methods=['GET', 'POST'])
def new_file():
    if request.method == 'POST':
        filename = request.form['filename']
        content = request.form['content']
        # 保存新建的文件到指定路径
        file_path = os.path.join(app.root_path, 'static', filename)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        return redirect('/upload')  # 重定向到/upload路由
    else:
        return render_template('newfile.html')
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            # 保存上传的文件到指定路径
            filename = secure_filename(file.filename)
            # 使用 latin-1 编码处理文件名
            if sys.version_info.major < 3:
                filename = filename.decode('utf-8').encode('latin-1')
            else:
                filename = filename.encode('latin-1').decode('latin-1')
            file.save(os.path.join(app.root_path, 'static', filename))
            return redirect('/upload')
    else:
        # 获取static目录下的所有文件和子目录
        file_list_html = list_files(os.path.join(app.root_path, 'static'))
        # 构建完整的HTML页面
        return render_template('upload.html', file_list_html=file_list_html)

@app.route('/edit/<path:filename>', methods=['GET', 'POST'])
def edit_file(filename):
    file_path = os.path.join(app.root_path, 'static', filename)
    if request.method == 'POST':
        content = request.form['content']
        with open(file_path, 'w',encoding='utf-8') as file:
            file.write(content)
        return redirect('/upload')  # 重定向到/upload路由
    else:
        with open(file_path, 'r',encoding='utf-8') as file:
            content = file.read()
        return render_template('edit.html', filename=filename, content=content)

@app.route('/delete/<path:filename>', methods=['GET', 'POST'])
def delete_file2(filename):
    file_path = os.path.join(app.root_path, 'static', filename)
    if request.method == 'POST':
        os.remove(file_path)
        return redirect('/upload')  # 重定向到/upload路由
    else:
        return render_template('delete.html', filename=filename)
@app.route('/rename/<path:filename>', methods=['GET', 'POST'])
def rename_file(filename):
    file_path = os.path.join(app.root_path, 'static', filename)
    if request.method == 'POST':
        new_filename = request.form.get('new_filename')
        new_file_path = os.path.join(app.root_path, 'static', new_filename)
        os.rename(file_path, new_file_path)
        return redirect('/upload')  # 重定向到文件上传页面
    else:
        return render_template('rename.html', filename=filename)



@app.route('/api', methods=['POST'])
def api():
    data = request.get_json()
    text = data['text']
    response = {
        'text': text
    }
    return jsonify(response)



#完美的分界线




# 从配置文件中settings加载配置
app.config.from_pyfile('set.py')
 
 
 

     
 
        
@app.route("/")
def index():
    return render_template("index.html")


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
