# 第一阶段：构建
FROM docker.1ms.run/node:20-alpine as builder

WORKDIR /web

# 先复制 package.json 和 yarn.lock
COPY web/package.json web/yarn.lock* ./

# 安装依赖（利用缓存）
RUN yarn install --registry=https://registry.npmmirror.com

# 复制源代码
COPY web/ .

# 构建
RUN yarn build

# 第二阶段：Nginx 运行时
FROM docker.1ms.run/nginx:alpine

COPY ./docker_env/nginx/my.conf /etc/nginx/conf.d/my.conf
COPY --from=builder /web/dist /usr/share/nginx/html
