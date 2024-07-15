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
import pymysql 
import pexpect
app = Flask(__name__, static_folder='static', static_url_path='/static')
# MySQL数据库配置
app.config['MYSQL_HOST'] = 'mysql.sqlpub.com'
app.config['MYSQL_USER'] = 'dakaca007'
app.config['MYSQL_PASSWORD'] = 'Kgds63EecpSlAtYR'
app.config['MYSQL_DB'] = 'dakaca'
@app.route('/php', methods=['GET', 'POST'])
def indexphp():
    if request.method == 'POST':
        php_code = request.form.get('php_code')
        # 创建临时文件存储 PHP 代码
        with open('temp.php', 'w', encoding='utf-8') as f:
            f.write(php_code)

        # 执行 PHP 代码
        try:
            # 在这里添加设置 PHP 内部编码的代码
            result = subprocess.check_output(['php', '-d', 'mbstring.internal_encoding=UTF-8', 'temp.php'], stderr=subprocess.STDOUT)
            result = result.decode('utf-8')  # 解码输出结果
        except subprocess.CalledProcessError as e:
            result = f"Error: {e.output.decode('utf-8')}"

        return render_template('indexphp.html', php_code=php_code, result=result)
    else:
        return render_template('indexphp.html')

@app.route("/ls")
def linxuls():
    return render_template('linuxls.html')  # 仅返回表单页面

@app.route("/execute_command", methods=["POST"])
def execute_command():
    command = request.form.get("command")  # 获取用户输入的命令
    if not command:
        return "请输入要执行的命令"

    try:
        output = subprocess.check_output(command.split())  # 执行命令
        return render_template('linuxls.html', html_content=output.decode("utf-8"))
    except subprocess.CalledProcessError as e:
        return f"命令执行失败: {e.output.decode('utf-8')}"  # 处理错误
@app.route("/")
def index():


    # 定义参数字典
    params = {'user_name': 'John Doe', 'product_id': '12345'}
    # 构建参数列表
    param_list = ['php', 'index.php']
    for key, value in params.items():
        param_list.append(f'{key}={value}')
    # 执行 PHP 脚本，并将参数传递给它
    process = subprocess.check_output(param_list)
    # 获取 PHP 脚本输出的 HTML 内容
    html_content = process.decode('utf-8')
    # 在 Flask 模板中渲染 HTML 内容
    return render_template('index.html', html_content=html_content)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
