# Jenkins CI/CD Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 PIS 项目创建 Jenkins Pipeline，实现前后端独立构建、镜像推送至 Harbor、Docker Compose 部署。

**Architecture:** 前后端分离 Pipeline 设计。Backend 和 Frontend 各自独立构建镜像、推送 Harbor、SSH 部署。两个 Pipeline 可独立触发、互不影响。

**Tech Stack:** Jenkins Pipeline (Groovy), Docker, Harbor, Docker Compose, SSH

---

## File Structure

```
├── backend/
│   └── Jenkinsfile                    # 后端构建+部署Pipeline
├── web/
│   └── Jenkinsfile                    # 前端构建+部署Pipeline
└── .gitlab-ci.yml                    # 禁用GitLab CI
```

---

## Task 1: Create Backend Jenkinsfile

**Files:**
- Create: `backend/Jenkinsfile`

- [ ] **Step 1: Create backend/Jenkinsfile**

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
                            ssh -o StrictHostKeyChecking=no ${SSH_USER}@${SERVER_HOST} << 'EOF'
                            cd ${COMPOSE_PATH}
                            docker-compose pull dvadmin3-django
                            docker-compose up -d --no-deps dvadmin3-django
                            EOF
                        """
                    }
                }
            }
        }
    }

    post {
        failure {
            echo "Backend Pipeline failed! Check Jenkins logs."
        }
        success {
            echo "Backend deployed successfully!"
        }
    }
}
```

- [ ] **Step 2: Commit backend/Jenkinsfile**

```bash
git add backend/Jenkinsfile
git commit -m "feat(jenkins): add backend CI/CD pipeline"
```

---

## Task 2: Create Frontend Jenkinsfile

**Files:**
- Create: `web/Jenkinsfile`

- [ ] **Step 1: Create web/Jenkinsfile**

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
                    cd web
                    yarn install --registry=https://registry.npmmirror.com
                    yarn build
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
                            ssh -o StrictHostKeyChecking=no ${SSH_USER}@${SERVER_HOST} << 'EOF'
                            cd ${COMPOSE_PATH}
                            docker-compose pull dvadmin3-web
                            docker-compose up -d --no-deps dvadmin3-web
                            EOF
                        """
                    }
                }
            }
        }
    }

    post {
        failure {
            echo "Frontend Pipeline failed! Check Jenkins logs."
        }
        success {
            echo "Frontend deployed successfully!"
        }
    }
}
```

- [ ] **Step 2: Commit web/Jenkinsfile**

```bash
git add web/Jenkinsfile
git commit -m "feat(jenkins): add frontend CI/CD pipeline"
```

---

## Task 3: Disable GitLab CI

**Files:**
- Modify: `.gitlab-ci.yml`

- [ ] **Step 1: Modify .gitlab-ci.yml to disable GitLab CI**

```yaml
# Jenkins 接管 CI/CD，禁用 GitLab CI
workflow:
  rules:
    - when: never
```

- [ ] **Step 2: Commit .gitlab-ci.yml change**

```bash
git add .gitlab-ci.yml
git commit -m "chore: disable GitLab CI, use Jenkins instead"
```

---

## Task 4: Final Verification

- [ ] **Step 1: Verify all files created**

```bash
git status
```

Expected output:
```
new file:   backend/Jenkinsfile
new file:   web/Jenkinsfile
modified:   .gitlab-ci.yml
```

---

## Jenkins Configuration Summary (Manual Steps Required)

These steps must be done manually in Jenkins UI:

### 1. Add Credentials

**Harbor Credentials:**
- Type: Username with Password
- ID: `harbor-credentials`
- Username: (your Harbor username)
- Password: (your Harbor password)

**SSH Credentials:**
- Type: SSH Username with Private Key
- ID: `server-ssh-key`
- Username: (server SSH user)
- Private Key: (server SSH private key)

### 2. Create Backend Job
- New Item → Pipeline
- Name: `pis-backend`
- Branch: `*/develop`
- Script Path: `backend/Jenkinsfile`

### 3. Create Frontend Job
- New Item → Pipeline
- Name: `pis-web`
- Branch: `*/develop`
- Script Path: `web/Jenkinsfile`

### 4. Update Pipeline Variables

In each Jenkinsfile, update these placeholder values:
```groovy
HARBOR_URL = 'harbor.example.com'      // 替换为实际Harbor地址
HARBOR_PROJECT = 'pis'                  // 替换为实际项目名
SERVER_HOST = 'your-server-ip'          // 替换为实际服务器IP
```

---

## Spec Coverage Checklist

- [x] Backend Jenkinsfile (build, push, deploy)
- [x] Frontend Jenkinsfile (build, push, deploy)
- [x] GitLab CI disabled
- [x] Harbor push integration
- [x] SSH deployment
- [x] Manual Jenkins configuration guide
