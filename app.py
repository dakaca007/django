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
class MyForm(Form):
    text1 = StringField('目录', validators=[DataRequired()])
    text2 = StringField('文件名', validators=[DataRequired()])
    text3 = StringField('内容', validators=[DataRequired()])
    submit = SubmitField('提交')
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
 
@app.route('/admin')
def editor():
    
    return render_template('editor.html')
@app.route('/admin2')
def editor2():
    current_directory = os.getcwd()
    return f"当前文件所在目录：{current_directory}"
@app.route('/opens', methods=['POST'])
def open_file():
    form = MyForm()
    file_path = request.form['file_path']
    try:
        if os.path.exists(file_path) and os.access(file_path, os.R_OK):
            #os.chdir(file_path)  # 更改当前工作目录
            with open(file_path, 'r',encoding='utf-8') as file:
                content = file.read()
            return render_template('editor2.html', content=content,form=form)
        else:
            return '文件不存在或无法访问'
    except FileNotFoundError:
        return '文件不存在'
    except PermissionError:
        return '无权限访问文件'
@app.route('/open', methods=['POST'])
def executeo():

    form=MyForm()
    directory = request.form['file_path']
    if directory=='':
        directory='/app/'
    else:
        directory=directory
        
        
    try:
        os.chdir(directory)  # 改变工作目录为表单字段的值
        command = request.form['command']
        
        result = subprocess.check_output(command, shell=True)
        result = result.decode('utf-8')  # 将字节流转换为字符串
        return render_template('editor2.html', result=result,form=form)
    except Exception as e:
        error_message = str(e)
        return render_template('indexcm.html', error_message=error_message)   
        
     


@app.route('/save', methods=['POST'])
def save_file():
    form = MyForm(request.form)
    if form.validate_on_submit():
        text1 = form.text1.data
        text2 = form.text2.data
        text3 = form.text3.data
        return f'提交的文本为：{text3}'
    else:
        return '表单验证失败'
    #content = request.form['content']
    content=text3


    
    #file_path = request.form['file_path2']
    file_path = text1
    if file_path=='':
        file_path='/app/'
    else:
        file_path=file_path
    #file_name = request.form['filename2']
    file_name = text2
    os.chdir(file_path)

    # 使用bash命令保存文件
    command = f'echo "{content}" > {file_name}'
    command = command.encode('utf-8')
    #subprocess.check_output(command, shell=True)
    result = subprocess.check_output(command, shell=True)
    result = result.decode('utf-8')  # 将字节流转换为字符串
    return render_template('editor.html', result=result)



@app.route('/reboot', methods=['POST'])
def reboot_flask():
    content = "/app/"
     
    os.chdir(content)

    # 使用bash命令保存文件
    command = f'python3 app2.py'
    command = command.encode('utf-8')
    #subprocess.check_output(command, shell=True)
    result = subprocess.check_output(command, shell=True)
    result = result.decode('utf-8')  # 将字节流转换为字符串
    return render_template('editor.html', result=result)   



@app.route('/kill', methods=['POST'])
def kill_flask():
    jincheng = request.form['jincheng']
    content = "/app/"
     
    os.chdir(content)

    # 使用bash命令保存文件
    command = f'kill -9 {jincheng}'
    command = command.encode('utf-8')
    #subprocess.check_output(command, shell=True)
    result = subprocess.check_output(command, shell=True)
    result = result.decode('utf-8')  # 将字节流转换为字符串
    return render_template('editor.html', result=result)   

     

@app.route('/delete', methods=['POST'])
def delete_file():
    file_path = request.form['file_path']
    if os.path.exists(file_path):
        os.remove(file_path)
        return '文件已删除'
    else:
        return '文件不存在'
        
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
