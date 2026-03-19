# 使用非Alpine源,兼容SQL Server安装
FROM python:3.10-slim

# 3. 安装系统依赖 (替换原来的 apk 命令)
# 注意：这里安装了构建依赖和微软驱动所需的依赖
RUN apt-get update && apt-get install -y \
    bash \
    git \
    curl \
    gnupg \
    ca-certificates \
    # 以下为原 apk 中的开发库对应的 apt 包名 (可能需微调)
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

# 4. 添加微软软件源和密钥 (解决 msodbcsql17 安装问题)
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /etc/apt/trusted.gpg.d/microsoft.gpg \
    && echo "deb [arch=amd64] https://packages.microsoft.com/repos/microsoft-ubuntu-focal-prod focal main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /backend
COPY ./backend/ .
RUN ls ./conf/
RUN awk 'BEGIN { cmd="cp -i ./conf/env.example.py   ./conf/env.py "; print "n" |cmd; }'
RUN sed -i "s|DATABASE_HOST = '127.0.0.1'|DATABASE_HOST = '177.10.0.1'|g" ./conf/env.py
RUN sed -i "s|REDIS_HOST = '127.0.0.1'|REDIS_HOST = '177.10.0.1'|g" ./conf/env.py
RUN python3 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt
CMD ["sh","docker_start.sh"]
