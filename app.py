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
import mysql.connector
app = Flask(__name__, static_folder='static', static_url_path='/static')
cnx = mysql.connector.connect(
    user='dakaca007',
    password='Kgds63EecpSlAtYR',
    host='mysql.sqlpub.com:3306',
    database='dakaca'
)       
@app.route("/")
def index():
    return render_template("index.html")
@app.route("/test")
def test():
    return render_template("test.html")
@app.route('/query')
def query_data():
    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM user")
    data = cursor.fetchall()
    cursor.close()
    return render_template('result.html', data=data)
 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
