# 使用官方 PHP 镜像作为基础镜像
FROM php:7.4-apache

# 安装常用扩展
RUN apt-get update && apt-get install -y \
    git \
    zip \
    unzip \
    curl \
    libpng-dev \
    libonig-dev \
    libxml2-dev \
    libzip-dev

# 安装 PHP 扩展
RUN docker-php-ext-install pdo_mysql mbstring exif pcntl bcmath gd zip

# 设置 Apache 配置
COPY apache2.conf /etc/apache2/apache2.conf
RUN a2enmod rewrite

# 设置 PHP 配置
COPY php.ini /usr/local/etc/php/php.ini

# 安装 Composer
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer

# 设置工作目录
WORKDIR /var/www/html

# 复制应用代码到容器中
COPY index.php /var/www/html

# 安装项目依赖
RUN composer install --no-interaction

# 设置文件权限
RUN chown -R www-data:www-data /var/www/html/storage

# 暴露端口
EXPOSE 80

# 启动 Apache 服务
CMD ["apache2-foreground"]
