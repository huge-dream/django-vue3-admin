# 第一阶段：构建
FROM docker.1ms.run/node:20-alpine as builder

WORKDIR /web/
COPY web/. .

# 使用 npmmirror 加速 yarn install
RUN yarn install --registry=https://registry.npmmirror.com
RUN yarn build

# 第二阶段：Nginx 运行时
FROM docker.1ms.run/nginx:alpine

COPY ./docker_env/nginx/my.conf /etc/nginx/conf.d/my.conf
COPY --from=builder /web/dist /usr/share/nginx/html
