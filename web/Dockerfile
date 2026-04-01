# 第一阶段：构建
FROM node:20-alpine as builder

WORKDIR /web

# 安装 pnpm
RUN npm install -g pnpm --registry=https://registry.npmmirror.com

# 先复制 package.json 和 pnpm-lock.yaml（build context 是项目根目录）
COPY web/package.json web/pnpm-lock.yaml* ./

# 安装依赖（利用缓存）
RUN pnpm install --registry=https://registry.npmmirror.com --frozen-lockfile

# 复制源代码
COPY web/ .

# 构建
RUN pnpm build

# 第二阶段：Nginx 运行时
FROM docker.1ms.run/nginx:alpine

# nginx.conf 由 docker-compose volumes 映射，无需复制
COPY --from=builder /web/dist /usr/share/nginx/html
