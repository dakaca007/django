# 使用官方的 PHP Apache 镜像作为基础镜像
FROM php:apache

# 更新包列表并安装 Python 和必要的依赖项
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安装 Flask
RUN pip3 install Flask
RUN pip3 install pymysql
RUN pip3 install requests
RUN pip3 install Werkzeug

RUN pip3 install wtforms
RUN pip3 install pexpect
WORKDIR /var/www/html/
# 启用 Apache mod_rewrite
RUN a2enmod rewrite
COPY . /var/www/html/
# 复制 Apache 配置文件
COPY 000-default.conf /etc/apache2/sites-available/000-default.conf
# 暴露 80 端口
EXPOSE 80
# 启动脚本
#CMD ["bash", "start.sh"]
# 启动 Apache 服务器
#CMD ["apache2-foreground"]
# 启动 Flask 应用和 Apache 服务器
CMD service apache2 start && python3 /var/www/html/app.py



