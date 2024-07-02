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
# 执行 PHP 脚本并返回结果
def execute_php_script(script_name, params=None):
    command = ['php','-d','mbstring.internal_encoding=UTF-8', script_name]
    if params:
        for key, value in params.items():
            command.append(f'--{key}={value}')
    try:
        result = subprocess.check_output(command, stderr=subprocess.STDOUT)
         
        return json.loads(result.decode('utf-8'))
    except subprocess.CalledProcessError as e:
        return f"Error: {e.output.decode('utf-8')}"
@app.route('/users', methods=['GET'])
def get_users():
    result = execute_php_script('get_users.php')
    return render_template('users.html', result=result)

@app.route('/users/add', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        params = {
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'email': request.form['email']
        }
        result = execute_php_script('add_user.php', params)
        return redirect(url_for('get_users'))
    return render_template('add_user.html')

@app.route('/users/update/<int:id>', methods=['GET', 'POST'])
def update_user(id):
    if request.method == 'POST':
        params = {
            'id': id,
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'email': request.form['email']
        }
        result = execute_php_script('update_user.php', params)
        return redirect(url_for('get_users'))
    params = {'id': id}
    user_data = execute_php_script('get_user.php', params)
    return render_template('update_user.html', user=user_data)

@app.route('/users/delete/<int:id>', methods=['POST'])
def delete_user(id):
    params = {'id': id}
    result = execute_php_script('delete_user.php', params)
    return redirect(url_for('get_users'))

@app.route('/c', methods=['GET', 'POST'])
def indexc():
    if request.method == 'POST':
        c_code = request.form.get('c_code')
        user_input = request.form.get('user_input')
        temp_file_path = 'temp.c'

        try:
            # 写入C代码到临时文件
            with open(temp_file_path, 'w', encoding='utf-8') as f:
                f.write(c_code)

            # 编译C代码
            subprocess.check_output(['gcc', temp_file_path, '-o', 'temp', '-std=c99', '-fexec-charset=UTF-8'], stderr=subprocess.STDOUT)

            # 启动编译后的C程序并进行交互
            chatbot = pexpect.spawn('./temp')

            try:
                # 发送用户输入到C程序
                chatbot.sendline(user_input)

                # 等待并读取C程序的响应
                chatbot.expect('\n', timeout=10)
                response = chatbot.before.decode('utf-8').strip()
                
                chatbot.terminate()  # 确保终止C程序进程

                return render_template('indexc.html', c_code=c_code, user_input=user_input, result=response)

            except pexpect.TIMEOUT:
                chatbot.terminate()
                return render_template('indexc.html', c_code=c_code, user_input=user_input, result='Chatbot did not respond in time.')

            except Exception as e:
                chatbot.terminate()
                return render_template('indexc.html', c_code=c_code, user_input=user_input, result=f'An error occurred: {str(e)}')

        except FileNotFoundError as e:
            return render_template('indexc.html', c_code=c_code, user_input=user_input, result=f'Error: Could not create temporary file: {e}')

        except subprocess.CalledProcessError as e:
            return render_template('indexc.html', c_code=c_code, user_input=user_input, result=f'Error: {e.output.decode("utf-8")}')

    else:
        return render_template('indexc.html')
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
    # 执行 PHP 脚本
    #process = subprocess.check_output(['php', 'index.php'])
    # 获取 PHP 脚本输出的 HTML 内容
    #html_content = process.decode('utf-8')
    # 在 Flask 模板中渲染 HTML 内容
    #return render_template('index.html', html_content=html_content)

    # 假设您想向 index.php 传递一个参数 'user_name' 为 'John Doe'
    #params = ['John Doe', '12345']
    # 执行 PHP 脚本，并将参数传递给它
    #process = subprocess.check_output(['php', 'index.php'] + params)
    # 获取 PHP 脚本输出的 HTML 内容
    #html_content = process.decode('utf-8')
    # 在 Flask 模板中渲染 HTML 内容
    #return render_template('index.html', html_content=html_content)

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
@app.route("/user_list")
def user_list():
    # 创建数据库连接
    conn = pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        db=app.config['MYSQL_DB'],
        charset='utf8'
    )   
    # 创建游标
    cursor = conn.cursor()
    # 执行SQL查询
    cursor.execute("SELECT * FROM user")
    data = list(cursor.fetchall())
    
     
    
    # 关闭游标和数据库连接
    cursor.close()
    conn.close()
     
     
    user_list_html = "<ul>"
    for user in data:
        user_list_html += f"<li>{user[1]} {user[2]} - {user[0]}"
        user_list_html += f"<a href='/delete_user/{user[0]}'>删除</a>"
        user_list_html += f" <a href='/update_user/{user[0]}'>更新</a></li>"
        user_list_html += f" <a href='/get_user/{user[0]}'>查询</a></li>"
    user_list_html += "</ul>"
    
    # 以 HTML 格式返回用户列表
    return render_template("user_list.html", user_list_html=user_list_html)
'''
@app.route("/add_user", methods=["POST"])
def add_user():
    # 获取POST请求中的数据
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    # 创建数据库连接
    conn = pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        db=app.config['MYSQL_DB'],
        charset='utf8'
    )
    
    # 创建游标
    cursor = conn.cursor()
    # 执行插入操作
    cursor.execute("INSERT INTO user (first_name, last_name, email) VALUES (%s, %s, %s)", (first_name, last_name, email))
    # 提交事务
    conn.commit()
    # 关闭游标和数据库连接
    cursor.close()
    conn.close()
    return "User added successfully"

@app.route("/delete_user/<int:user_id>", methods=["GET"])

def delete_user(user_id):
    # 创建数据库连接
    conn = pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        db=app.config['MYSQL_DB'],
        charset='utf8'
    )
    
    # 创建游标
    cursor = conn.cursor()
    # 执行删除操作
    cursor.execute("DELETE FROM user WHERE id = %s", (user_id,))
    # 提交事务
    conn.commit()
    # 关闭游标和数据库连接
    cursor.close()
    conn.close()
    return redirect("/user_list")
 
@app.route("/update_user/<int:user_id>", methods=["GET","POST"])
def update_user(user_id):
    if request.method == "POST":
        # 获取POST请求中的数据
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        # 创建数据库连接
        conn = pymysql.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            db=app.config['MYSQL_DB'],
            charset='utf8'
        )
        # 创建游标
        cursor = conn.cursor()
        # 执行更新操作
        cursor.execute("UPDATE user SET first_name = %s, last_name = %s, email = %s WHERE id = %s", (first_name, last_name, email, user_id))
        # 提交事务
        conn.commit()
        # 关闭游标和数据库连接
        cursor.close()
        conn.close()
        # 重定向到用户列表或其他页面
        return redirect("/user_list")
    else:
        # 返回带有用户ID的模板，用于显示更新用户信息的表单
        return render_template("update_user.html", user_id=user_id)
@app.route("/get_user/<int:user_id>", methods=["GET"])
def get_user(user_id):
    # 创建数据库连接
    conn = pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        db=app.config['MYSQL_DB'],
        charset='utf8'
    )
    
    # 创建游标
    cursor = conn.cursor()
    # 执行查询操作
    cursor.execute("SELECT * FROM user WHERE id = %s", (user_id,))
    data = cursor.fetchone()
    # 关闭游标和数据库连接
    cursor.close()
    conn.close()
    if data:
        result = {
            'id': data[0],
            'first_name': data[1],
            'last_name': data[2],
            'email': data[3]
        }
         
        result2=json.dumps(result, ensure_ascii=False)  # 禁止使用 ASCII 编码
        return render_template('user_info.html', users=result2)
    else:
        return "User not found"
'''
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
