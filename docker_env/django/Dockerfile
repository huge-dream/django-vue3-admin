FROM registry.cn-zhangjiakou.aliyuncs.com/dvadmin-pro/dvadmin3-base-backend:latest
WORKDIR /backend
COPY ./backend/ .
RUN ls ./conf/
RUN awk 'BEGIN { cmd="cp -i ./conf/env.example.py   ./conf/env.py "; print "n" |cmd; }'
RUN sed -i "s|DATABASE_HOST = '127.0.0.1'|DATABASE_HOST = '177.10.0.1'|g" ./conf/env.py
RUN sed -i "s|REDIS_HOST = '127.0.0.1'|REDIS_HOST = '177.10.0.1'|g" ./conf/env.py
RUN python3 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt
CMD ["sh","docker_start.sh"]
