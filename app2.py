# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, render_template, Response
import requests
import subprocess
import json
import os

app = Flask(__name__)

 
@app.route('/')
def index():
    return render_template('new.html')
 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
