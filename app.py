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
app.config['MYSQL_HOST'] = 'mysql.sqlpub.com:3306'
app.config['MYSQL_USER'] = 'dakaca007'
app.config['MYSQL_PASSWORD'] = 'Kgds63EecpSlAtYR'
app.config['MYSQL_DB'] = 'dakaca'


@app.route("/")
def index():
    return render_template("index.html")
@app.route("/test")
def test():
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
    data = cursor.fetchall()
    
    # 处理查询结果
    result = []
    for row in data:
        result.append({
            'id': row[0],
            'first_name': row[1],
            'last_name':row[2],
            'email': row[3]
        })
    
    # 关闭游标和数据库连接
    cursor.close()
    conn.close()
    return {'data': result}
 
 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
