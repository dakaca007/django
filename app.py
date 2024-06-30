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
        db=app.config['MYSQL_DB']
    )   
    # 创建游标
    cursor = conn.cursor()
    # 执行SQL查询
    cursor.execute("SELECT * FROM user")
    data = list(cursor.fetchall())
    
     
    
    # 关闭游标和数据库连接
    cursor.close()
    conn.close()
     
     

    # 或者以 JSON 数据的形式返回查询结果
    return render_template("user_list.html", users=data)
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
        db=app.config['MYSQL_DB']
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
        db=app.config['MYSQL_DB']
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

    return "User deleted successfully"
 

@app.route("/update_user/<int:user_id>", methods=["POST"])
def update_user(user_id):
    # 获取POST请求中的数据
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")

    # 创建数据库连接
    conn = pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        db=app.config['MYSQL_DB']
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

    return "User updated successfully"
@app.route("/get_user/<int:user_id>", methods=["GET"])
def get_user(user_id):
    # 创建数据库连接
    conn = pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        db=app.config['MYSQL_DB']
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
        return jsonify(result)
    else:
        return "User not found"
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
