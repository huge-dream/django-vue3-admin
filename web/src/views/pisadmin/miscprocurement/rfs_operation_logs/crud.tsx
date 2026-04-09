import { useI18n } from 'vue-i18n'
import { CreateCrudOptionsProps, CreateCrudOptionsRet } from '@fast-crud/fast-crud'
import * as api from './api'

export const createCrudOptions = function ({ crudExpose, context: _ctx }: CreateCrudOptionsProps): CreateCrudOptionsRet {
  const { t } = useI18n()

  const operationTypeLabels = (): Record<number, string> => ({
    1: t('message.pages.rfs_operation_logs.operationType.1'),
    2: t('message.pages.rfs_operation_logs.operationType.2'),
    3: t('message.pages.rfs_operation_logs.operationType.3'),
    4: t('message.pages.rfs_operation_logs.operationType.4'),
    5: t('message.pages.rfs_operation_logs.operationType.5'),
    6: t('message.pages.rfs_operation_logs.operationType.6'),
    7: t('message.pages.rfs_operation_logs.operationType.7'),
    8: t('message.pages.rfs_operation_logs.operationType.8'),
    9: t('message.pages.rfs_operation_logs.operationType.9'),
    10: t('message.pages.rfs_operation_logs.operationType.10'),
  })

  const purchaseTypeLabels = (): Record<number, string> => ({
    1: t('message.pages.rfs_operation_logs.purchaseType.1'),
    2: t('message.pages.rfs_operation_logs.purchaseType.2'),
  })

  const emptyText = () => t('message.pages.rfs_operation_logs.formatter.empty')
  const noQuotationText = () => t('message.pages.rfs_operation_logs.formatter.noQuotation')

  const formatStatusChange = (per: unknown, cur: unknown) => {
    const a = String(per ?? '').trim()
    const b = String(cur ?? '').trim()
    if (!a && !b) return emptyText()
    if (!a) return `${b || emptyText()}`
    if (!b) return `${a} → ${emptyText()}`
    return `${a} → ${b}`
  }

  void crudExpose
  void _ctx
  return {
    crudOptions: {
      form: {
        labelWidth: '110px'
      },
      request: {
        pageRequest: async (query) => api.GetList(query)
      },
      table: {
        rowKey: 'id',
        stripe: true,
        border: true
      },
      actionbar: {
        buttons: {
          add: { show: false }
        }
      },
      rowHandle: {
        show: false
      },
      columns: {
        inquiry_no: {
          title: t('message.pages.rfs_operation_logs.table.columns.inquiry_no'),
          type: 'text',
          search: {
            show: true,
            component: { props: { placeholder: t('message.pages.rfs_operation_logs.placeholder.inquiry_no'), clearable: true } }
          },
          form: { show: false },
          column: { minWidth: 130, showOverflowTooltip: true }
        },
        buyer: {
          title: t('message.pages.rfs_operation_logs.table.columns.buyer'),
          type: 'text',
          search: {
            show: true,
            component: { props: { placeholder: t('message.pages.rfs_operation_logs.placeholder.buyer'), clearable: true } }
          },
          form: { show: false },
          column: { show: false }
        },
        purchase_type: {
          title: t('message.pages.rfs_operation_logs.table.columns.purchase_type'),
          type: 'text',
          search: { show: false },
          form: { show: false },
          column: {
            width: 88,
            formatter: ({ row }: { row: any }) => {
              const n = Number(row?.purchase_type)
              return purchaseTypeLabels()[n] ?? (row?.purchase_type != null ? String(row.purchase_type) : emptyText())
            }
          }
        },
        operation_time: {
          title: t('message.pages.rfs_operation_logs.table.columns.operation_time'),
          type: 'datetime',
          search: { show: false },
          form: { show: false },
          column: {
            width: 168,
            showOverflowTooltip: true,
            sortable: 'custom'
          }
        },
        operation_type: {
          title: t('message.pages.rfs_operation_logs.table.columns.operation_type'),
          type: 'text',
          search: { show: false },
          form: { show: false },
          column: {
            width: 130,
            showOverflowTooltip: true,
            formatter: ({ row }: { row: any }) => {
              const n = Number(row?.operation_type)
              if (!Number.isFinite(n) || n <= 0) return emptyText()
              return operationTypeLabels()[n] || `${n}`
            }
          }
        },
        operation_user: {
          title: t('message.pages.rfs_operation_logs.table.columns.operation_user'),
          type: 'text',
          search: { show: false },
          form: { show: false },
          column: {
            width: 110,
            showOverflowTooltip: true,
            formatter: ({ row }: { row: any }) => {
              const s = String(row?.operation_user ?? '').trim()
              return s || emptyText()
            }
          }
        },
        status_change: {
          title: t('message.pages.rfs_operation_logs.table.columns.status_change'),
          type: 'text',
          search: { show: false },
          form: { show: false },
          column: {
            minWidth: 160,
            showOverflowTooltip: true,
            formatter: ({ row }: { row: any }) => formatStatusChange(row?.per_status, row?.cur_status)
          }
        },
        operation_desc: {
          title: t('message.pages.rfs_operation_logs.table.columns.operation_desc'),
          type: 'text',
          search: { show: false },
          form: { show: false },
          column: { minWidth: 180, showOverflowTooltip: true }
        },
        quotation_no: {
          title: t('message.pages.rfs_operation_logs.table.columns.quotation_no'),
          type: 'text',
          search: { show: false },
          form: { show: false },
          column: {
            width: 116,
            showOverflowTooltip: true,
            formatter: ({ row }: { row: any }) => {
              const q = String(row?.quotation_no ?? '').trim()
              return q && q !== '-' ? q : noQuotationText()
            }
          }
        }
      }
    }
  }
}
