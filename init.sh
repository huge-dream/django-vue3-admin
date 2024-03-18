#!/bin/bash
ENV_FILE=".env"
# 检查 .env 文件是否存在
if [ -f "$ENV_FILE" ]; then
    echo "$ENV_FILE 文件已存在。"
else
    # 生成MYSQL随机密码
    MYSQL_PASSWORD=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 18)
    echo "MYSQL_PASSWORD=$MYSQL_PASSWORD" >> "$ENV_FILE"
    echo "MYSQL随机密码已生成并写入 $ENV_FILE 文件。"
    # 生成REDIS随机密码
    REDIS_PASSWORD=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 12)
    # 将密码写入 .env 文件
    echo "REDIS_PASSWORD=$REDIS_PASSWORD" >> "$ENV_FILE"
    echo "REDIS随机密码已生成并写入 $ENV_FILE 文件。"
    
    awk 'BEGIN { cmd="cp -i ./backend/conf/env.example.py   ./backend/conf/env.py "; print "n" |cmd; }'
    sed -i "s|DATABASE_HOST = '127.0.0.1'|DATABASE_HOST = '177.10.0.13'|g" ./backend/conf/env.py
    sed -i "s|REDIS_HOST = '127.0.0.1'|REDIS_HOST = '177.10.0.15'|g" ./backend/conf/env.py
    sed -i "s|DATABASE_PASSWORD = 'DVADMIN3'|DATABASE_PASSWORD = '$MYSQL_PASSWORD'|g" ./backend/conf/env.py
    sed -i "s|REDIS_PASSWORD = 'DVADMIN3'|REDIS_PASSWORD = '$REDIS_PASSWORD'|g" ./backend/conf/env.py
    echo "初始化密码创建成功"
fi

docker-compose up -d
docker exec dvadmin3-django python manage.py makemigrations
docker exec dvadmin3-django python manage.py migrate
docker exec dvadmin3-django python manage.py init
echo "欢迎使用dvadmin3项目"
echo "登录地址：http://ip:8080"
echo "如访问不到，请检查防火墙配置"
