

# dvadmin3-build

## 介绍
一款适用于**django-vue3-admin** 编译打包exe、macOS的dmg文件等打包工具。支持加密代码、一键启动项目，无需考虑环境。

**dvadmin3-build** 是一个方便的工具，用于将**django-vue3-admin**项目编译打包为可执行文件（如exe）或macOS的dmg文件等。它提供了以下好处：

- 方便的部署：使用**dvadmin3-build**，您无需担心环境依赖和配置问题。您可以将整个项目打包为一个可执行文件或者安装包，方便快速部署在任何支持的操作系统上。

- 代码加密：**dvadmin3-build** 支持代码加密，可以将您的项目源代码加密为二进制格式，增加代码的安全性和保护知识产权。

- 一键启动项目：打包后的可执行文件或安装包可以通过简单的双击来启动项目，无需手动设置和配置环境，减少了部署和启动的复杂性。

- 跨平台支持：**dvadmin3-build** 可以将**django-vue3-admin**项目打包为适用于多个操作系统的可执行文件或安装包，包括Windows、macOS、Ubuntu、中标麒麟等操作系统中。

- 易于使用：**dvadmin3-build** 提供了简单易懂的命令行界面，使得打包过程更加简便和高效。只需一个简单的命令，即可完成项目的打包。



## 功能支持项

- [ ] 支持平台
  - [x] Windows
  - [x] MacOS
  - [ ] Ubuntu
  - [ ] 中标麒麟
- [ ] 支持功能
  - [x] 一键启动 dvadmin3
  - [x] 托盘最小化
  - [ ] dvadmin 初始化
  - [ ] 数据库配置
  - [ ] 端口配置
  - [ ] 支持celery异步模块
  - [ ] 进程守护

## 功能及使用方法

### 安装依赖
pip install dvadmin3_build-1.0.0-py3-none-any.whl

### 前端编译
yarn run build:local

### 后端
#### settings.py 中添加模块
~~~
INSTALLED_APPS = [
   ...
    "dvadmin3_build"
]

HIDDEN_IMPORTS = [
  'xxxx' # 添加 app 中自己的模块，用于编译
]
~~~

#### 迁移与初始化(项目已迁移过的不再需要)
~~~
python manage.py makemigrations
python manage.py migrate
python manage.py init
python manage.py init_data
~~~
#### 编译
~~~
# 编译后位于 dist 目录
python manage.py build 
# windows 打包需要安装 InstallForgeSetup.exe，使用 dvadmin3_InstallForge.ifp 模板（dvadmin3_build/windows_build_tools 目录下）
# InstallForge 打包教程：https://www.pythonguis.com/tutorials/packaging-pyqt6-applications-windows-pyinstaller/#setup
~~~
