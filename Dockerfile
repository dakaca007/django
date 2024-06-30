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
# 指定pip源（清华源）
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple --upgrade pip
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple --upgrade setuptools
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple --upgrade wheel
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple pipenv
RUN pipenv install -i https://pypi.tuna.tsinghua.edu.cn/simple --skip-lock --system --python 3.8

 
# 创建并配置Session存储
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple Flask-Session
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple pymysql 
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple pyramid
 

 
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple flask

RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple requests
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple Werkzeug

RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple wtforms



# 暴露端口
EXPOSE 80


# 启动脚本
CMD ["bash", "start.sh"]
