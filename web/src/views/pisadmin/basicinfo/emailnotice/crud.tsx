import { dict, CreateCrudOptionsProps, CreateCrudOptionsRet } from '@fast-crud/fast-crud'
import { ElMessage } from 'element-plus'
import * as api from './api'

const statusDict = [
  { value: 'pending', label: '待发送' },
  { value: 'sending', label: '发送中' },
  { value: 'success', label: '已发送' },
  { value: 'failed', label: '发送失败' }
]

const joinEmails = (value: unknown) => {
  if (!Array.isArray(value)) return ''
  return value.filter((v) => !!v).join('; ')
}

const formatAttachments = (value: unknown) => {
  if (!Array.isArray(value)) return ''
  const names = value
    .map((v: any) => v?.name || v?.file_name || v?.filename || v?.key || '')
    .filter((v: any) => !!v)
  if (names.length === 0) return value.length ? `${value.length} 个附件` : ''
  return names.join('; ')
}

export const createCrudOptions = function ({ crudExpose }: Partial<CreateCrudOptionsProps>): CreateCrudOptionsRet {
  return {
    crudOptions: {
      request: {
        pageRequest: async (query) => api.GetList(query)
      },
      form: {
        labelWidth: '120px'
      },
      actionbar: {
        buttons: {
          add: { show: false }
        }
      },
      rowHandle: {
        fixed: 'right',
        width: 300,
        buttons: {
          resend: {
            text: '重送',
            type: 'warning',
            order: 1,
            show: ({ row }) => row.status !== 'sending',
            async click({ row }) {
              try {
                const res: any = await api.Resend(row.id)
                const ok = res?.success === true || res?.code === 0
                const detailMsg =
                  res?.detail?.error || res?.detail?.message || res?.msg || res?.message || '处理完成'
                if (ok) {
                  ElMessage.success(detailMsg || '重送成功')
                } else {
                  ElMessage.error(detailMsg || '重送失败')
                }
                crudExpose?.doRefresh?.()
              } catch (e: any) {
                const msg =
                  e?.response?.data?.detail?.error ||
                  e?.response?.data?.error ||
                  e?.response?.data?.msg ||
                  e?.message ||
                  '重送失败'
                ElMessage.error(msg)
              }
            }
          }
        }
      },
      columns: {
        subject: {
          title: '邮件主题',
          type: 'text',
          search: { show: true, component: { props: { placeholder: '请输入主题', clearable: true } } },
          column: { minWidth: 220, showOverflowTooltip: true }
        },
        biz_type: {
          title: '业务类型',
          type: 'text',
          search: { show: true, component: { props: { placeholder: '业务类型/模块', clearable: true } } },
          column: { minWidth: 140, showOverflowTooltip: true }
        },
        biz_id: {
          title: '业务标识',
          type: 'text',
          search: { show: true, component: { props: { placeholder: '业务单号/ID', clearable: true } } },
          column: { minWidth: 160, showOverflowTooltip: true }
        },
        to_emails: {
          title: '收件人',
          type: 'text',
          column: { minWidth: 220, showOverflowTooltip: true, formatter: ({ value }) => joinEmails(value) }
        },
        cc_emails: {
          title: '抄送',
          type: 'text',
          column: { minWidth: 180, showOverflowTooltip: true, formatter: ({ value }) => joinEmails(value) }
        },
        bcc_emails: {
          title: '密送',
          type: 'text',
          column: { minWidth: 180, showOverflowTooltip: true, formatter: ({ value }) => joinEmails(value) }
        },
        status: {
          title: '发送状态',
          type: 'dict-select',
          dict: dict({ data: statusDict }),
          search: { show: true, component: { props: { clearable: true, placeholder: '请选择状态' } } },
          column: { width: 120 }
        },
        sent_at: {
          title: '发送时间',
          type: 'datetime',
          search: {
            show: true,
            component: {
              props: {
                type: 'datetimerange',
                valueFormat: 'YYYY-MM-DD HH:mm:ss',
                startPlaceholder: '开始时间',
                endPlaceholder: '结束时间'
              }
            }
          },
          column: { width: 180 }
        },
        attachments: {
          title: '附件',
          type: 'text',
          column: { minWidth: 160, showOverflowTooltip: true, formatter: ({ value }) => formatAttachments(value) }
        },
        last_error: {
          title: '错误信息',
          type: 'text',
          column: { minWidth: 240, showOverflowTooltip: true }
        },
        message_id: {
          title: '消息ID',
          type: 'text',
          column: { minWidth: 180, showOverflowTooltip: true }
        },
        retry_count: {
          title: '重试次数',
          type: 'number',
          column: { width: 100 }
        },
        create_datetime: {
          title: '创建时间',
          type: 'datetime',
          form: { show: false },
          column: { width: 180 }
        }
      }
    }
  }
}
