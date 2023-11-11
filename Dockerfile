# 使用官方的CentOS 7镜像作为基础
FROM centos:7

# 安装Python 3和pip
RUN yum install -y epel-release && yum install -y python3 && yum install -y python3-pip

# 安装SSH服务器
RUN yum install -y openssh-server

# 设置root用户的密码（这里设置为"password"，你可以根据需要修改）
RUN echo 'root:password' | chpasswd

# 启用SSH服务
RUN systemctl enable sshd

# 设置工作目录
WORKDIR /app

# 将当前目录中的所有文件复制到工作目录
COPY . /app

RUN pip3 install flask
RUN pip3 install requests

# 暴露端口
EXPOSE 80 22

# 运行应用程序和SSH服务器
CMD service sshd start && python3 app.py
