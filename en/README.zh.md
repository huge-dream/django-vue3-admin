# Django-Vue3-Admin

[](https://gitee.com/liqianglog/django-vue-admin/blob/master/LICENSE)![img](https://img.shields.io/badge/license-MIT-blue.svg)[](https://python.org/)![img](https://img.shields.io/badge/python-%3E=3.7.x-green.svg)[](https://docs.djangoproject.com/zh-hans/3.2/)![PyPI - Django Version badge](https://img.shields.io/badge/django%20versions-3.2-blue)[](https://nodejs.org/zh-cn/)![img](https://img.shields.io/badge/node-%3E%3D%2012.0.0-brightgreen)[](https://gitee.com/liqianglog/django-vue-admin)![img](https://gitee.com/liqianglog/django-vue-admin/badge/star.svg?theme=dark)

[Preview](https://demo.dvadmin.com) | [Official Documentation](https://www.django-vue-admin.com) | [Group Chat](https://qm.qq.com/cgi-bin/qm/qr?k=fOdnHhC8DJlRHGYSnyhoB8P5rgogA6Vs&jump_from=webapi) | [Community](https://bbs.django-vue-admin.com) | [Plugin Market](https://bbs.django-vue-admin.com/plugMarket.html) | [Github](https://github.com/liqianglog/django-vue-admin)

💡 **"About"**

We are a group of young people who love code. In this hot era, we hope to calm down and bring a little bit of our color and color through code.

Because of love, embrace the future!

## Platform Introduction

💡 [django-vue3-admin](https://gitee.com/huge-dream/django-vue3-admin.git) is a set of fully open source rapid development platforms, which are free for individual use and authorized for group use without reservation. django-vue3-admin is a complete set of basic development platforms based on the permission control of the RBAC model. The permission granularity reaches the column level, and the front-end and back-end are separated. The back-end uses django + django-rest-framework, and the front-end uses vue3 + CompositionAPI + typescript + vite + element plus

- 🧑‍🤝‍🧑The front end uses Vue3+TS+pinia+fastcrud (thanks to [vue-next-admin](https://lyt-top.gitee.io/vue-next-admin-doc-preview/) )
- 👭The backend uses Python language Django framework and the powerful [Django REST Framework](https://pypi.org/project/djangorestframework) .
- 👫Authorization uses [Django REST Framework SimpleJWT](https://pypi.org/project/djangorestframework-simplejwt) and supports multi-terminal authentication system.
- 👬Supports loading dynamic permission menu, easy permission control in multiple ways.
- 👬New column permission management, with granularity down to each column.
- 💏Special thanks to: [vue-next-admin](https://lyt-top.gitee.io/vue-next-admin-doc-preview/) .
- 💡Special thanks to [JetBrains](https://www.jetbrains.com/) for providing free IntelliJ IDEA license for this open source project.

#### 🏭 Environmental Support

Edge | Firefox | Chrome | Safari
--- | --- | --- | ---
Edge ≥ 79 | Firefox ≥ 78 | Chrome ≥ 64 | Safari ≥ 12

> Since Vue3 no longer supports IE11, ElementPlus also does not support IE11 and earlier versions.

## Online Experience

👩‍👧‍👦Demo address: [https://demo.dvadmin.com](https://demo.dvadmin.com)

- Account: superadmin

- Password: admin123456

👩‍👦‍👦Document address: [DVAdmin official website](https://www.django-vue-admin.com)

## comminicate

- Communication community: [Click me](https://bbs.django-vue-admin.com) 👩‍👦‍👦

- Plugin Market: [Click me](https://bbs.django-vue-admin.com/plugMarket.html) 👩‍👦‍👦

- Django-vue-admin chat group 01 (full): 812482043 [Click the link to join the group chat](https://qm.qq.com/cgi-bin/qm/qr?k=aJVwjDvH-Es4MPJQuoO32N0SucK22TE5&jump_from=webapi)

- Django-vue-admin chat group 02 (full): 687252418 [Click the link to join the group chat](https://qm.qq.com/cgi-bin/qm/qr?k=4jJN4IjWGfxJ8YJXbb_gTsuWjR34WLdc&jump_from=webapi)

- django-vue-admin chat group 03: 442108213 [click the link to join the group chat](http://qm.qq.com/cgi-bin/qm/qr?_wv=1027&k=wsm5oSz3K8dElBYUDtLTcQSEPhINFkl8&authKey=M6sbER0z59ZakgBr5erFeZyFZU15CI52bErNZa%2FxSvvGIuVAbY0N5866v89hm%2FK4&noverify=0&group_code=442108213)

- QR code


    <img src="https://images.gitee.com/uploads/images/2022/0530/233203_5fb11883_5074988.jpeg" width="200">

## Source code address

Gitee address (main): [https://gitee.com/huge-dream/django-vue3-admin](https://gitee.com/huge-dream/django-vue3-admin) 👩‍👦‍👦

GitHub address: [https://github.com/huge-dream/django-vue3-admin](https://github.com/huge-dream/django-vue3-admin) 👩‍👦‍👦

## Built-in functions

1. 👨‍⚕️Menu management: configure system menus, operation permissions, button permission identification, backend interface permissions, etc.
2. 🧑‍⚕️Department management: configure system organization (company, department, role).
3. 👩‍⚕️Role management: role menu permission allocation, data permission allocation, set roles to divide data range permissions by department.
4. 🧑‍🎓Button permission control: Authorize the button permissions and interface permissions of the role, so that each interface can authorize the data range.
5. 🧑‍🎓Field column permission control: field display permissions on the authorization page, specifically the display permissions of a certain column.
6. 👨‍🎓User management: The user is the system operator, and this function mainly completes the system user configuration.
7. 👬Interface whitelist: configure interfaces that do not require permission verification.
8. 🧑‍🔧Dictionary management: Maintain some relatively fixed data that is frequently used in the system.
9. 🧑‍🔧Regional management: management of provinces, cities and counties.
10. 📁Attachment management: unified management of all files, pictures, etc. on the platform.
11. 🗓️Operation log: system normal operation log record and query; system abnormal information log record and query.
12. [🔌Plugin Market](https://bbs.django-vue-admin.com/plugMarket.html) : Applications and plugins developed based on the Django-Vue-Admin framework.

## Plugin Market 🔌

Updating...

## Warehouse branch description 💈

Main branch: master (stable version) Development branch: develop

## Preparation

```
Python >= 3.11.0 (最低3.9+版本)
nodejs >= 16.0
Mysql >= 8.0 (可选，默认数据库sqlite3，支持5.7+，推荐8.0版本)
Redis (可选，最新版)
```

## Frontend ♝

```bash
# 克隆项目
git clone https://gitee.com/huge-dream/django-vue3-admin.git

# 进入项目目录
cd web

# 安装依赖
npm install yarn
yarn install --registry=https://registry.npmmirror.com

# 启动服务
yarn build
# 浏览器访问 http://localhost:8080
# .env.development 文件中可配置启动端口等参数
# 构建生产环境
# yarn run build
```

## Backend 💈

```bash
1. 进入项目目录 cd backend
2. 在项目根目录中，复制 ./conf/env.example.py 文件为一份新的到 ./conf 文件夹下，并重命名为 env.py
3. 在 env.py 中配置数据库信息
	mysql数据库版本建议：8.0
	mysql数据库字符集：utf8mb4
4. 安装依赖环境
	pip3 install -r requirements.txt
5. 执行迁移命令：
	python3 manage.py makemigrations
	python3 manage.py migrate
6. 初始化数据
	python3 manage.py init
7. 初始化省市县数据:
	python3 manage.py init_area
8. 启动项目
	python3 manage.py runserver 0.0.0.0:8000
或使用 uvicorn :
  uvicorn application.asgi:application --port 8000 --host 0.0.0.0 --workers 8
```

## Development suggestions

The backend and web are each opened in a separate window for development

### Visit Project

- Access address: [http://localhost:8080](http://localhost:8080) (this address is used by default, if modified, please follow the configuration file)
- Account: `superadmin` Password: `admin123456`

### docker-compose run

```shell
# 先安装docker-compose (自行百度安装),执行此命令等待安装，如有使用celery插件请打开docker-compose.yml中celery 部分注释
docker-compose up -d
# 初始化后端数据(第一次执行即可)
docker exec -ti dvadmin3-django bash
python manage.py makemigrations
python manage.py migrate
python manage.py init_area
python manage.py init
exit

前端地址：http://127.0.0.1:8080
后端地址：http://127.0.0.1:8080/api
# 在服务器上请把127.0.0.1 换成自己公网ip
账号：superadmin 密码：admin123456

# docker-compose 停止
docker-compose down
#  docker-compose 重启
docker-compose restart
#  docker-compose 启动时重新进行 build
docker-compose up -d --build
```

## Demo Picture✅

![image-01](https://foruda.gitee.com/images/1701348994587355489/1bc749e7_5074988.png)

![image-02](https://foruda.gitee.com/images/1701349037811908960/80d361db_5074988.png)

![image-03](https://foruda.gitee.com/images/1701349224478845203/954f0a7b_5074988.png)

![image-04](https://foruda.gitee.com/images/1701349248928658877/64926724_5074988.png)

![image-05](https://foruda.gitee.com/images/1701349259068943299/1306ba40_5074988.png)

![image-06](https://foruda.gitee.com/images/1701349294894429495/e3b3a8cf_5074988.png)

![image-07](https://foruda.gitee.com/images/1701350432536247561/3b26685e_5074988.png)

![image-08](https://foruda.gitee.com/images/1701350455264771992/b364c57f_5074988.png)

![image-09](https://foruda.gitee.com/images/1701350479266000753/e4e4f7c5_5074988.png)

![image-10](https://foruda.gitee.com/images/1701350501421625746/f8dd215e_5074988.png)
