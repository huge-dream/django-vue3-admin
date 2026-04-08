import { dict, CreateCrudOptionsProps, CreateCrudOptionsRet } from '@fast-crud/fast-crud'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'
import * as api from './api'

const joinEmails = (value: unknown) => {
  if (!Array.isArray(value)) return ''
  return value.filter((v) => !!v).join('; ')
}

export const createCrudOptions = function ({ crudExpose }: Partial<CreateCrudOptionsProps>): CreateCrudOptionsRet {
  const { t } = useI18n()

  const statusDict = [
    { value: 'pending', label: t('message.pages.basicinfo.emailnotice.statusPending') },
    { value: 'sending', label: t('message.pages.basicinfo.emailnotice.statusSending') },
    { value: 'success', label: t('message.pages.basicinfo.emailnotice.statusSuccess') },
    { value: 'failed', label: t('message.pages.basicinfo.emailnotice.statusFailed') }
  ]

  const formatAttachments = (value: unknown) => {
    if (!Array.isArray(value)) return ''
    const names = value
      .map((v: any) => v?.name || v?.file_name || v?.filename || v?.key || '')
      .filter((v: any) => !!v)
    if (names.length === 0) return value.length ? `${value.length} ${t('message.pages.basicinfo.emailnotice.attachments')}` : ''
    return names.join('; ')
  }

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
            text: t('message.pages.basicinfo.emailnotice.resend'),
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
                  ElMessage.success(detailMsg || `${t('message.pages.basicinfo.emailnotice.resend')}${t('message.pages.basicinfo.emailnotice.success')}`)
                } else {
                  ElMessage.error(detailMsg || `${t('message.pages.basicinfo.emailnotice.resend')}${t('message.pages.basicinfo.emailnotice.failed')}`)
                }
                crudExpose?.doRefresh?.()
              } catch (e: any) {
                const msg =
                  e?.response?.data?.detail?.error ||
                  e?.response?.data?.error ||
                  e?.response?.data?.msg ||
                  e?.message ||
                  `${t('message.pages.basicinfo.emailnotice.resend')}${t('message.pages.basicinfo.emailnotice.failed')}`
                ElMessage.error(msg)
              }
            }
          }
        }
      },
      columns: {
        subject: {
          title: t('message.pages.basicinfo.emailnotice.subject'),
          type: 'text',
          search: { show: true, component: { props: { placeholder: t('message.pages.basicinfo.emailnotice.subject'), clearable: true } } },
          column: { minWidth: 220, showOverflowTooltip: true }
        },
        biz_type: {
          title: t('message.pages.basicinfo.emailnotice.bizType'),
          type: 'text',
          search: { show: true, component: { props: { placeholder: t('message.pages.basicinfo.emailnotice.bizType'), clearable: true } } },
          column: { minWidth: 140, showOverflowTooltip: true }
        },
        biz_id: {
          title: t('message.pages.basicinfo.emailnotice.bizId'),
          type: 'text',
          search: { show: true, component: { props: { placeholder: t('message.pages.basicinfo.emailnotice.bizId'), clearable: true } } },
          column: { minWidth: 160, showOverflowTooltip: true }
        },
        to_emails: {
          title: t('message.pages.basicinfo.emailnotice.toEmails'),
          type: 'text',
          column: { minWidth: 220, showOverflowTooltip: true, formatter: ({ value }) => joinEmails(value) }
        },
        cc_emails: {
          title: t('message.pages.basicinfo.emailnotice.ccEmails'),
          type: 'text',
          column: { minWidth: 180, showOverflowTooltip: true, formatter: ({ value }) => joinEmails(value) }
        },
        bcc_emails: {
          title: t('message.pages.basicinfo.emailnotice.bccEmails'),
          type: 'text',
          column: { minWidth: 180, showOverflowTooltip: true, formatter: ({ value }) => joinEmails(value) }
        },
        status: {
          title: t('message.pages.basicinfo.emailnotice.status'),
          type: 'dict-select',
          dict: dict({ data: statusDict }),
          search: { show: true, component: { props: { clearable: true, placeholder: t('message.pages.basicinfo.emailnotice.status') } } },
          column: { width: 120 }
        },
        sent_at: {
          title: t('message.pages.basicinfo.emailnotice.sentAt'),
          type: 'datetime',
          search: {
            show: true,
            component: {
              props: {
                type: 'datetimerange',
                valueFormat: 'YYYY-MM-DD HH:mm:ss',
                startPlaceholder: t('message.pages.system.common.startTime'),
                endPlaceholder: t('message.pages.system.common.endTime')
              }
            }
          },
          column: { width: 180 }
        },
        attachments: {
          title: t('message.pages.basicinfo.emailnotice.attachments'),
          type: 'text',
          column: { minWidth: 160, showOverflowTooltip: true, formatter: ({ value }) => formatAttachments(value) }
        },
        last_error: {
          title: t('message.pages.basicinfo.emailnotice.lastError'),
          type: 'text',
          column: { minWidth: 240, showOverflowTooltip: true }
        },
        message_id: {
          title: t('message.pages.basicinfo.emailnotice.messageId'),
          type: 'text',
          column: { minWidth: 180, showOverflowTooltip: true }
        },
        retry_count: {
          title: t('message.pages.basicinfo.emailnotice.retryCount'),
          type: 'number',
          column: { width: 100 }
        },
        create_datetime: {
          title: t('message.pages.basicinfo.emailnotice.createTime'),
          type: 'datetime',
          form: { show: false },
          column: { width: 180 }
        }
      }
    }
  }
}
