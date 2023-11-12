#!/bin/bash

# 启动Django开发服务器
python3 manage.py runserver 0.0.0.0:8000 &

# 启动Flask应用程序
python3 app.py
