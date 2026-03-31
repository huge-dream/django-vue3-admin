# Jenkins CI/CD Pipeline 设计

## 概述

为 PIS 采购询报价管理系统配置 Jenkins 持续集成/持续部署，实现前后端独立构建、镜像推送至 Harbor、私有服务器 Docker Compose 部署。

## 技术栈

| 组件 | 技术 |
|------|------|
| 后端 | Django 4.2 + DRF + uWSGI |
| 前端 | Node.js + Vite + TypeScript |
| 数据库 | MySQL 8.0 |
| 队列 | Redis 6.2 + Celery |
| 镜像仓库 | Harbor (私有) |
| 部署方式 | Docker Compose |

## 架构设计

```
GitLab (develop branch)
       │
       ▼
┌─────────────────────────────────────┐
│         Jenkins Master              │
├─────────────────────────────────────┤
│  ┌──────────────┐ ┌──────────────┐  │
│  │ Backend Jenkinsfile │ │Web Jenkinsfile │  │
│  └───────┬───────┘ └───────┬──────┘  │
│          │                  │         │
│          ▼                  ▼         │
│    ┌──────────┐      ┌──────────┐    │
│    │ Build &  │      │ Build &  │    │
│    │ Push to  │      │ Push to  │    │
│    │ Harbor   │      │ Harbor   │    │
│    └────┬─────┘      └────┬─────┘    │
│         └────────┬────────┘           │
│                  ▼                    │
│           Docker Compose              │
│           远程服务器                   │
└─────────────────────────────────────┘
```

## Pipeline 设计

### 1. Backend Pipeline (`backend/Jenkinsfile`)

#### 环境变量

| 变量 | 说明 | 示例值 |
|------|------|--------|
| HARBOR_URL | Harbor 仓库地址 | harbor.example.com |
| HARBOR_PROJECT | Harbor 项目名 | pis |
| IMAGE_NAME | 镜像名 | dvadmin3-django |
| SERVER_HOST | 部署服务器IP | 192.168.1.100 |
| COMPOSE_PATH | docker-compose 路径 | /mnt/data/pis |

#### 构建阶段

| Stage | 步骤 | 命令 |
|-------|------|------|
| Checkout | 拉取后端代码 | `git clone` |
| Build | 构建 Django 镜像 | `docker build -f docker_env/django/Dockerfile -t ${IMAGE_TAG}` |
| Push | 推送镜像到 Harbor | `docker push ${IMAGE_TAG}` |
| Deploy | SSH 远程部署 | `ssh ${SERVER_HOST} "cd ${COMPOSE_PATH} && docker-compose pull && docker-compose up -d --no-deps dvadmin3-django"` |

#### Jenkinsfile 模板

```groovy
pipeline {
    agent any

    environment {
        HARBOR_URL = 'harbor.example.com'
        HARBOR_PROJECT = 'pis'
        IMAGE_NAME = 'dvadmin3-django'
        SERVER_HOST = 'your-server-ip'
        COMPOSE_PATH = '/mnt/data/pis'
        CREDENTIALS_ID = 'harbor-credentials'
        SSH_CREDENTIALS_ID = 'server-ssh-key'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Image') {
            steps {
                script {
                    def imageTag = "${HARBOR_URL}/${HARBOR_PROJECT}/${IMAGE_NAME}:${BUILD_NUMBER}"
                    env.IMAGE_TAG = imageTag
                    sh """
                        docker build -f docker_env/django/Dockerfile \
                            -t ${imageTag} .
                    """
                }
            }
        }

        stage('Push to Harbor') {
            steps {
                script {
                    withCredentials([usernamePassword(
                        credentialsId: CREDENTIALS_ID,
                        usernameVariable: 'HARBOR_USER',
                        passwordVariable: 'HARBOR_PASS'
                    )]) {
                        sh """
                            echo ${HARBOR_PASS} | docker login ${HARBOR_URL} -u ${HARBOR_USER} --password-stdin
                            docker push ${IMAGE_TAG}
                            docker logout ${HARBOR_URL}
                        """
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    withCredentials([sshUserPrivateKey(
                        credentialsId: SSH_CREDENTIALS_ID,
                        usernameVariable: 'SSH_USER',
                        privateKeyVariable: 'SSH_KEY'
                    )]) {
                        sh """
                            ssh -o StrictHostKeyChecking=no ${SSH_USER}@${SERVER_HOST} """
                            cd ${COMPOSE_PATH} && \\
                            docker-compose pull dvadmin3-django && \\
                            docker-compose up -d --no-deps dvadmin3-django
                            """
                        """
                    }
                }
            }
        }
    }

    post {
        failure {
            echo "Pipeline failed! Check Jenkins logs."
        }
    }
}
```

### 2. Frontend Pipeline (`web/Jenkinsfile`)

#### 构建阶段

| Stage | 步骤 | 命令 |
|-------|------|------|
| Checkout | 拉取前端代码 | `git clone` |
| Install | 安装依赖 | `npm install` |
| Build | 构建前端产物 | `npm run build` |
| Build Image | 构建 Nginx 镜像 | `docker build -f docker_env/web/Dockerfile -t ${IMAGE_TAG}` |
| Push | 推送镜像到 Harbor | `docker push ${IMAGE_TAG}` |
| Deploy | SSH 远程部署 | `ssh ${SERVER_HOST} "docker-compose up -d --no-deps dvadmin3-web"` |

#### Jenkinsfile 模板

```groovy
pipeline {
    agent any

    environment {
        HARBOR_URL = 'harbor.example.com'
        HARBOR_PROJECT = 'pis'
        IMAGE_NAME = 'dvadmin3-web'
        SERVER_HOST = 'your-server-ip'
        COMPOSE_PATH = '/mnt/data/pis'
        CREDENTIALS_ID = 'harbor-credentials'
        SSH_CREDENTIALS_ID = 'server-ssh-key'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install & Build') {
            steps {
                sh """
                    npm install
                    npm run build
                """
            }
        }

        stage('Build Image') {
            steps {
                script {
                    def imageTag = "${HARBOR_URL}/${HARBOR_PROJECT}/${IMAGE_NAME}:${BUILD_NUMBER}"
                    env.IMAGE_TAG = imageTag
                    sh """
                        docker build -f docker_env/web/Dockerfile \
                            -t ${imageTag} .
                    """
                }
            }
        }

        stage('Push to Harbor') {
            steps {
                script {
                    withCredentials([usernamePassword(
                        credentialsId: CREDENTIALS_ID,
                        usernameVariable: 'HARBOR_USER',
                        passwordVariable: 'HARBOR_PASS'
                    )]) {
                        sh """
                            echo ${HARBOR_PASS} | docker login ${HARBOR_URL} -u ${HARBOR_USER} --password-stdin
                            docker push ${IMAGE_TAG}
                            docker logout ${HARBOR_URL}
                        """
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    withCredentials([sshUserPrivateKey(
                        credentialsId: SSH_CREDENTIALS_ID,
                        usernameVariable: 'SSH_USER',
                        privateKeyVariable: 'SSH_KEY'
                    )]) {
                        sh """
                            ssh -o StrictHostKeyChecking=no ${SSH_USER}@${SERVER_HOST} """
                            cd ${COMPOSE_PATH} && \\
                            docker-compose pull dvadmin3-web && \\
                            docker-compose up -d --no-deps dvadmin3-web
                            """
                        """
                    }
                }
            }
        }
    }

    post {
        failure {
            echo "Pipeline failed! Check Jenkins logs."
        }
    }
}
```

## Jenkins 配置要求

### 1. 凭证配置

#### Harbor 凭证
- 类型：Username with Password
- ID：`harbor-credentials`
- 用户名/密码：Harbor 仓库账号

#### SSH 凭证
- 类型：SSH Username with Private Key
- ID：`server-ssh-key`
- 用户名：服务器 SSH 用户
- 私钥：服务器 SSH 私钥

### 2. Jenkins Job 配置

#### Backend Job
- 类型：Pipeline
- 源码管理：Git
- Repository URL：项目 Git 地址
- Branch：*/develop
- Script Path：backend/Jenkinsfile

#### Frontend Job
- 类型：Pipeline
- 源码管理：Git
- Repository URL：项目 Git 地址
- Branch：*/develop
- Script Path：web/Jenkinsfile

### 3. Docker 配置

Jenkins Agent 需要：
- Docker CLI 已安装
- Docker daemon 正常运行
- 可访问 Harbor 仓库

## Web Dockerfile 要求

需要在 `web/docker_env/web/Dockerfile` 创建 Nginx 镜像：

```dockerfile
FROM nginx:alpine
COPY dist/ /usr/share/nginx/html/
COPY docker_env/nginx/conf.d /etc/nginx/conf.d/
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## GitLab CI 禁用

在 `.gitlab-ci.yml` 开头添加：

```yaml
# Jenkins 接管 CI/CD，禁用 GitLab CI
workflow:
  rules:
    - when: never
```

或者直接删除 `.gitlab-ci.yml` 文件。

## 部署流程

1. 开发者 push 代码到 `develop` 分支
2. Jenkins 自动触发 Pipeline
3. 前后端独立构建镜像
4. 镜像推送到 Harbor
5. SSH 登录部署服务器
6. 执行 `docker-compose pull` 拉取新镜像
7. 执行 `docker-compose up -d` 重启服务
8. Jenkins Job 显示成功/失败状态

## 未来扩展

- [ ] 添加单元测试阶段
- [ ] 添加 SonarQube 代码审查
- [ ] 添加钉钉/企业微信通知
- [ ] 添加镜像版本回滚功能
- [ ] 配置 Blue-Green Deployment
