# 使用官方的CentOS 7镜像作为基础
FROM centos:7

# 安装Python 3和pip
RUN yum install -y epel-release && yum install -y python3 && yum install -y python3-pip

# 安装gcc编译器
RUN yum install -y gcc
# 安装PHP解释器
RUN yum install -y php php-cli php-mysql
# 设置工作目录
WORKDIR /app

# 将当前目录中的所有文件复制到工作目录
COPY . /app

 

 

 
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple flask
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple pymysql
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple requests
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple Werkzeug

RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple wtforms
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple pexpect
 

# 暴露端口
EXPOSE 80


# 启动脚本
CMD ["bash", "start.sh"]
