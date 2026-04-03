# 报价截止时间到期邮件通知采购 — 设计文档

## 1. 需求概述

每 5 分钟轮询 `pissupplier.QuotationMaster`，找出已到期（`quote_deadline < now`）但仍未报价（`status ∈ {1 待报价, 2 报价中}`）的报价单，按**询价单维度**合并发送一封邮件给采购负责人，每天最多一次。

## 2. 触发条件

- **字段**：`pissupplier.QuotationMaster.quote_deadline` 和 `status`
- **逻辑**：`quote_deadline < now` 且 `status in (1, 2)`
- **轮询间隔**：Celery Beat 每 5 分钟

## 3. 通知逻辑

### 3.1 合并规则
- 按 `inquiry_no` 分组，同一询价单下所有到期未报价的供应商合并到一封邮件
- 避免邮件轰炸

### 3.2 去重规则
- 复用现有 `should_send_quote_timeout_reminder(inquiry_no, cooldown_hours=24)` 按 `inquiry_no` 做 24 小时冷却期
- 已发送过（EmailNotice.biz_type="inquiry_quote_timeout" + status="success"）的询价单跳过

### 3.3 收件人
- 仅「采购负责人」(buyer)，对应 Inquiry.buyer 字段
- 复用现有 `resolve_inquiry_purchaser_emails` 函数

### 3.4 邮件内容
- 字段：询价单名称、编号、报价截止时间、到期供应商列表、比价页面链接
- 模板：参考 `backend/templates/emails/quote_timeout_body.html`

## 4. 数据流

```
Celery Beat (每5分钟)
  └── check_quote_deadline_expired()  [Celery Task]
        ├── 查询所有 status∈{1,2} 且 quote_deadline < now 的 QuotationMaster
        ├── 按 inquiry_no 分组
        ├── 对每个 inquiry_no：
        │     ├── 检查24h冷却期（should_send_quote_timeout_reminder）
        │     ├── 查找 Inquiry，获取采购负责人邮箱
        │     ├── 渲染邮件内容（过期供应商列表）
        │     └── 发送邮件（send_email_notice）
        └── 写 EmailNotice 记录（biz_type="inquiry_quote_timeout"）
```

## 5. 新增文件

| 文件路径 | 说明 |
|---|---|
| `backend/apps/pisadmin/miscprocurement/tasks.py` | Celery 定时任务：轮询报价截止时间、发送邮件 |

## 6. 修改文件

| 文件路径 | 修改内容 |
|---|---|
| `backend/application/celery.py` | 注册 Celery Beat Schedule（新增 `check_quote_deadline_expired` 任务） |

## 7. 核心任务函数签名

```python
@app.task
def check_quote_deadline_expired() -> dict:
    """
    Celery Beat 定时任务：轮询报价截止时间已到期的报价单，
    按询价单合并发送邮件通知采购负责人，每天最多一次。

    Returns: {"checked": N, "sent": M, "skipped": K}
    """
```

## 8. Celery Beat Schedule 配置

```python
CELERY_BEAT_SCHEDULE = {
    "check-quote-deadline-expired": {
        "task": "apps.pisadmin.miscprocurement.tasks.check_quote_deadline_expired",
        "schedule": crontab(minute="*/5"),  # 每5分钟
    },
}
```

## 9. 已有可复用代码

- `apps.pisadmin.basicinfo.views.email_utils.send_quote_timeout_notice_to_purchaser` — 单封邮件发送
- `apps.pisadmin.basicinfo.views.email_utils.should_send_quote_timeout_reminder` — 24h冷却期判断
- `apps.pisadmin.basicinfo.views.email_utils.resolve_inquiry_purchaser_emails` — 采购负责人邮箱解析
- `apps.pisadmin.basicinfo.views.email_utils.send_email_notice` — 邮件发送底层
- `backend/templates/emails/quote_timeout_body.html` — 邮件模板

## 10. 异常处理

- 邮件发送失败不影响其他询价单处理，记录异常日志
- Celery 任务失败自动重试（最多3次，间隔3分钟）
