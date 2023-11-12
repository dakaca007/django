#!/bin/bash

# 启动Django开发服务器
# 启动PHP-FPM
php-fpm start &

# 启动Flask应用程序
python3 app.py
