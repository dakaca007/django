FROM ubuntu:22.04

# 替换APT为阿里云镜像源
RUN sed -i 's/archive.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    sed -i 's/security.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list

# 安装基础依赖
RUN apt update && DEBIAN_FRONTEND=noninteractive apt install -y \
    build-essential \
    python3 \
    python3-pip \
    python3-dev \
    nodejs \
    npm \
    bash \
    git \
    && rm -rf /var/lib/apt/lists/*

# 创建工作目录
WORKDIR /app

# 复制应用代码
COPY ./flaskapp /app

# 使用阿里云PyPI镜像安装Python依赖
RUN python3 -m pip install --no-cache-dir -r requirements.txt \
    -i https://mirrors.aliyun.com/pypi/simple/ \
    --trusted-host mirrors.aliyun.com

# 安装前端依赖
RUN npm config set registry https://registry.npmmirror.com && \
    npm install -g socket.io-client@4.5.1 ace-builds@1.4.12

# 创建代码沙箱目录
RUN mkdir -p /tmp/code && \
    chmod 777 /tmp/code

# 设置环境变量
ENV FLASK_SECRET=your-secret-key-here
ENV FLASK_ENV=production

# 暴露端口
EXPOSE 80

# 启动命令（使用SocketIO运行）
CMD ["python3", "app.py"]
