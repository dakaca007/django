FROM ubuntu:22.04

# 安装基础依赖（移除Nginx和不必要工具）
RUN apt update && DEBIAN_FRONTEND=noninteractive apt install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# 创建工作目录
WORKDIR /app

# 复制应用代码和依赖文件
COPY ./flaskapp /app
COPY ./flaskapp/requirements.txt /app/requirements.txt

# 安装Python依赖
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# 暴露Flask默认端口
EXPOSE 80

# 启动命令（假设使用Flask内置服务器）
CMD ["python3", "app.py"]