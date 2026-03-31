# 第一阶段：构建依赖
FROM docker.1ms.run/python:3.10-slim as builder

WORKDIR /backend

# 安装构建依赖
RUN apt-get update && apt-get install -y \
    bash \
    git \
    curl \
    gnupg \
    ca-certificates \
    libjpeg-dev \
    libmariadb-dev-compat \
    default-libmysqlclient-dev \
    build-essential \
    libffi-dev \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libpcre2-dev \
    libncurses5-dev \
    libreadline-dev \
    tk-dev \
    libpq-dev \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# 添加微软源
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /etc/apt/trusted.gpg.d/microsoft.gpg \
    && echo "deb [arch=amd64] https://packages.microsoft.com/repos/microsoft-ubuntu-focal-prod focal main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && rm -rf /var/lib/apt/lists/*

COPY ./backend/ .
RUN ls ./conf/
RUN awk 'BEGIN { cmd="cp -i ./conf/env.example.py   ./conf/env.py "; print "n" |cmd; }'
RUN sed -i "s|DATABASE_HOST = '127.0.0.1'|DATABASE_HOST = '177.10.0.1'|g" ./conf/env.py
RUN sed -i "s|REDIS_HOST = '127.0.0.1'|REDIS_HOST = '177.10.0.1'|g" ./conf/env.py
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt

# 第二阶段：运行时镜像
FROM docker.1ms.run/python:3.10-slim

COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /backend /backend

WORKDIR /backend
CMD ["sh","docker_start.sh"]
