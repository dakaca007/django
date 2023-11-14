# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, render_template, Response
import requests
import subprocess
import json
import os

app = Flask(__name__)

 
@app.route('/ef')
def indexef():
    return render_template('new.html')
@app.route('/')
def index():
    # 调用PHP脚本并获取输出
    result = subprocess.check_output(['php', 'index.php'])
    return result
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
