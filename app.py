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
app = Flask(__name__, static_folder='static', static_url_path='/static')
# MySQL数据库配置
app.config['MYSQL_HOST'] = 'mysql.sqlpub.com'
app.config['MYSQL_USER'] = 'dakaca007'
app.config['MYSQL_PASSWORD'] = 'Kgds63EecpSlAtYR'
app.config['MYSQL_DB'] = 'dakaca'
@app.route("/")
def index():
    return render_template("index.html")
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
         
        return json.dumps(result, ensure_ascii=False)  # 禁止使用 ASCII 编码
    else:
        return "User not found"
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
