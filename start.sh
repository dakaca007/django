#!/bin/bash
python3 p.py &    # 后台启动爬虫
python3 app.py    # 前台启动 Flask，保持容器运行
