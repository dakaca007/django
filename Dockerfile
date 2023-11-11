# 使用官方的CentOS 7镜像作为基础
FROM centos:7

# 安装Python 3和pip
RUN yum install -y epel-release && yum install -y python3 && yum install -y python3-pip

# 设置工作目录
WORKDIR /app

# 将当前目录中的所有文件复制到工作目录
COPY . /app

RUN pip3 install flask
RUN pip3 install requests

# 暴露端口
EXPOSE 80 8080 8000 22

# 运行应用程序
CMD ["python3", "app.py"]
