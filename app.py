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
         
@app.route("/")
def index():
    return render_template("index.html")
@app.route("/test")
def test():
    return render_template("test.html")

 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
