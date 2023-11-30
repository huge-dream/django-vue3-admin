# Django-Vue3-Admin

[![img](https://img.shields.io/badge/license-MIT-blue.svg)](https://gitee.com/huge-dream/django-vue3-admin/blob/master/LICENSE)  [![img](https://img.shields.io/badge/python-%3E=3.7.x-green.svg)](https://python.org/)  [![PyPI - Django Version badge](https://img.shields.io/badge/django%20versions-3.2-blue)](https://docs.djangoproject.com/zh-hans/3.2/) [![img](https://img.shields.io/badge/node-%3E%3D%2012.0.0-brightgreen)](https://nodejs.org/zh-cn/) [![img](https://gitee.com/huge-dream/django-vue3-admin/badge/star.svg?theme=dark)](https://gitee.com/huge-dream/django-vue3-admin)

[preview](https://demo.dvadmin.com) | [Official website document](https://www.django-vue-admin.com) | [qq group](https://qm.qq.com/cgi-bin/qm/qr?k=fOdnHhC8DJlRHGYSnyhoB8P5rgogA6Vs&jump_from=webapi) | [community](https://bbs.django-vue-admin.com) | [plugins market](https://bbs.django-vue-admin.com/plugMarket.html) | [Github](https://github.com/liqianglog/django-vue-admin)

💡 **「About」**

We are a group of young people who love Code. In this hot era, we hope to calm down and bring some of our colors and colors through code.

Because of love, so embrace the future

## framework introduction

💡 [django-vue3-admin](https://gitee.com/huge-dream/django-vue3-admin.git) Is a set of all open source rapid development platform, no reservation for individuals and enterprises free use.

* 🧑‍🤝‍🧑Front-end adoption Vue3+TS+pinia+fastcrud。
* 👭The backend uses the Python language Django framework as well as the powerful[Django REST Framework](https://pypi.org/project/djangorestframework)。
* 👫Permission authentication use[Django REST Framework SimpleJWT](https://pypi.org/project/djangorestframework-simplejwt)，Supports the multi-terminal authentication system.
* 👬Support loading dynamic permission menu, multi - way easy permission control.
* 💏 Special thanks: [vue-next-admin](https://lyt-top.gitee.io/vue-next-admin-doc-preview/).
* 💡 💏 Special thanks:[jetbrains](https://www.jetbrains.com/) To provide a free IntelliJ IDEA license for this open source project.

## Online experience

👩‍👧‍👦👩‍👧‍👦 demo address:[https://demo.dvadmin.com](https://demo.dvadmin.com)

* demo account：superadmin

* demo password：admin123456

👩‍👦‍👦docs:[https://django-vue-admin.com](https://django-vue-admin.com)

## communication

* Communication community:[click here](https://bbs.django-vue-admin.com)👩‍👦‍👦

* plugins market:[click here](https://bbs.django-vue-admin.com/plugMarket.html)👩‍👦‍👦

## source code url:

gitee(Main push)：[https://gitee.com/huge-dream/django-vue3-admin](https://gitee.com/huge-dream/django-vue3-admin)👩‍👦‍👦

github：no data

## core function

1. 👨‍⚕️ Menu management: Configure the system menu, operation permissions, button permissions, back-end interface permissions, etc.
2. 🧑‍⚕️ Department management: Configure the system organization (company, department, role).
3. 👩‍⚕️ Role management: role menu permission allocation, data permission allocation, set roles according to the department for data range permission division.
4. 🧑‍🎓 Rights Specifies the rights of the authorization role.
5. 👨‍🎓 User management: The user is the system operator, this function mainly completes the system user configuration.
6. 👬 Interface whitelist: specifies the interface that does not need permission verification.
7. 🧑‍🔧 Dictionary management: Maintenance of some fixed data frequently used in the system.
8. 🧑‍🔧 Regional management: to manage provinces, cities, counties and regions.
9. 📁 Attachment management: Unified management of all files and pictures on the platform.
10. 🗓 ️operation logs: log and query the system normal operation; Log and query system exception information.
    11.🔌 [plugins market] (<https://bbs.django-vue-admin.com/plugMarket.html>) : based on the Django framework - Vue - Admin application and plug-in development.

## plugins market 🔌

* Celery Asynchronous task：[dvadmin-celery](https://gitee.com/huge-dream/dvadmin-celery)
* Upgrade center backend：[dvadmin-upgrade-center](https://gitee.com/huge-dream/dvadmin-upgrade-center)
* Upgrade center front：[dvadmin-upgrade-center-web](https://gitee.com/huge-dream/dvadmin-upgrade-center-web)

## before start project you need:

~~~
Python >= 3.8.0 
nodejs >= 14.0
Mysql >= 5.7.0 (Optional. The default database is sqlite3. 8.0 is recommended)
Redis(Optional, the latest edition)
~~~

## frontend♝

```bash
# clone code
git clone https://gitee.com/huge-dream/django-vue3-admin.git

# enter code dir
cd web

# install dependence
npm install --registry=https://registry.npm.taobao.org

# Start service
npm run dev
# Visit http://localhost:8080 in your browser
# Parameters such as boot port can be configured in the #.env.development file
# Build the production environment
# npm run build
```

## backend💈

~~~bash
1. enter code dir cd backend
2. copy ./conf/env.example.py to ./conf dir，rename as env.py
3. in env.py configure database information
 mysql database recommended version: 8.0
 mysql database character set: utf8mb4
4. install pip dependence
 pip3 install -r requirements.txt
5. Execute the migration command:
 python3 manage.py makemigrations
 python3 manage.py migrate
6. Initialization data
 python3 manage.py init
7. Initialize provincial, municipal and county data:
 python3 manage.py init_area
8. start backend
 python3 manage.py runserver 0.0.0.0:8000
or daphne :
  daphne -b 0.0.0.0 -p 8000 application.asgi:application
~~~

### visit backend swagger

* visit url：[http://localhost:8080](http://localhost:8080) (The default address is this one. If you want to change it, follow the configuration file)
* account：`superadmin` password：`admin123456`

### docker-compose

~~~shell
docker-compose up -d
# Initialize backend data (first execution only)
docker exec -ti dvadmin-django bash
python manage.py makemigrations 
python manage.py migrate
python manage.py init_area
python manage.py init
exit

frontend url：http://127.0.0.1:8080
backend url：http://127.0.0.1:8080/api
# Change 127.0.0.1 to your own public ip address on the server
account：`superadmin` password：`admin123456`

# docker-compose stop
docker-compose down
#  docker-compose restart
docker-compose restart
#  docker-compose on start build
docker-compose up -d --build
~~~

## Demo screenshot✅

![image-01](https://images.gitee.com/uploads/images/2022/0530/234137_b58c8f98_5074988.png)

![image-02](https://images.gitee.com/uploads/images/2022/0530/234240_39834603_5074988.png)

![image-03](https://images.gitee.com/uploads/images/2022/0530/234339_35e728a0_5074988.png)

![image-04](https://images.gitee.com/uploads/images/2022/0530/234426_957036b0_5074988.png)

![image-05](https://images.gitee.com/uploads/images/2022/0530/234458_898be492_5074988.png)

![image-06](https://images.gitee.com/uploads/images/2022/0530/234521_35b40076_5074988.png)

![image-07](https://images.gitee.com/uploads/images/2022/0530/234615_c2325639_5074988.png)

![image-08](https://images.gitee.com/uploads/images/2022/0530/234639_1ed6cc93_5074988.png)

![image-09](https://images.gitee.com/uploads/images/2022/0530/234815_cea2c53f_5074988.png)

![image-10](https://images.gitee.com/uploads/images/2022/0530/234840_5f3e5f53_5074988.png)
