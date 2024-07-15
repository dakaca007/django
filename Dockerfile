# 使用官方的 PHP Apache 镜像作为基础镜像
FROM php:apache
WORKDIR /var/www/html/
# 启用 Apache mod_rewrite
# 安装 PHP PDO_MYSQL 扩展
RUN docker-php-ext-install mysqli pdo_mysql \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN a2enmod rewrite
COPY . /var/www/html/

# 暴露 80 端口
EXPOSE 80
# 启动脚本
#CMD ["bash", "start.sh"]
# 启动 Apache 服务器
CMD ["apache2-foreground"]

