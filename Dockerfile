# 使用官方的 PHP Apache 镜像作为基础镜像
FROM php:apache

# 更新包列表并安装 Python 和必要的依赖项
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安装 Flask
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple Flask
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple pymysql
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple requests
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple Werkzeug

RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple wtforms
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple pexpect
WORKDIR /var/www/html/
# 启用 Apache mod_rewrite
RUN a2enmod rewrite
COPY . /var/www/html/
# 暴露 80 端口
EXPOSE 80
# 启动脚本
#CMD ["bash", "start.sh"]
# 启动 Apache 服务器
CMD ["apache2-foreground"]


