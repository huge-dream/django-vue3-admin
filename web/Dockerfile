# 第一阶段：构建
FROM node:20-alpine as builder

WORKDIR /web

# 先复制 package.json 和 yarn.lock
COPY package.json yarn.lock* ./

# 安装依赖（利用缓存）
RUN yarn install --registry=https://registry.npmmirror.com

# 复制源代码
COPY . .

# 构建
RUN yarn build

# 第二阶段：Nginx 运行时
FROM docker.1ms.run/nginx:alpine

# nginx.conf 由 docker-compose volumes 映射，无需复制
COPY --from=builder /web/dist /usr/share/nginx/html
