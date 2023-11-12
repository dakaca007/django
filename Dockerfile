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
RUN pip3 install PyMySQL
RUN pip3 install flask_sqlalchemy
RUN pip3 install Flask-Login
RUN pip3 install Flask-WTF
RUN pip3 install django
RUN pip3 install numpy
RUN pip3 install beautifulsoup4



# 暴露端口
EXPOSE 80 8080 8000 22
RUN django-admin startproject project_name .

# 运行应用程序
CMD ["python3", "app.py"]
# 运行Django开发服务器
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
