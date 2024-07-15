# 构建阶段：使用 Node.js 构建前端资源
FROM node:16-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build # 运行你的构建脚本

# 运行阶段：使用 PHP Apache 镜像运行应用程序
FROM php:apache
WORKDIR /var/www/html/
# 启用 Apache mod_rewrite
# 安装 PHP PDO_MYSQL 扩展
RUN docker-php-ext-install pdo_mysql \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN a2enmod rewrite
# 复制构建好的前端资源
COPY --from=builder /app/build . 

# 暴露 80 端口
EXPOSE 80
# 启动脚本
#CMD ["bash", "start.sh"]
# 启动 Apache 服务器
CMD ["apache2-foreground"]


