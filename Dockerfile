# 使用官方的CentOS 7镜像作为基础
FROM centos:7

# 安装Python 3和pip
RUN yum install -y epel-release && yum install -y python3 && yum install -y python3-pip
# 安装gcc编译器
RUN yum install -y gcc

# 设置工作目录
WORKDIR /app

# 将当前目录中的所有文件复制到工作目录
COPY . /app

RUN pip3 install flask
RUN pip3 install requests
RUN pip3 install PyMySQL
RUN pip3 install django
RUN pip3 install numpy
RUN pip3 install beautifulsoup4
RUN django-admin startproject myapp .


# 暴露端口
EXPOSE 80


# 启动脚本
CMD ["bash", "start.sh"]
