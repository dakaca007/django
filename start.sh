#!/bin/bash
# 后台运行所有爬虫脚本
for script in p*.py; do
    if [[ "$script" == "app.py" ]]; then
        echo "启动: $script"
        python3 "$script" &
    fi
done
#python3 app.py    # 前台启动 Flask，保持容器运行
