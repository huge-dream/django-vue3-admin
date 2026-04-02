import { CreateCrudOptionsProps, CreateCrudOptionsRet } from '@fast-crud/fast-crud'
import * as api from './api'

/** 与后端 RFQOperationLogs.OPERATION_TYPE_CHOICES 一致 */
const OPERATION_TYPE_LABELS: Record<number, string> = {
  1: '询价单创建',
  2: '询价单确认',
  3: '询价单发布',
  4: '询价单还原',
  5: '报价截止',
  6: '供应商报价',
  7: '比议价',
  8: '议价审核提交',
  9: '议价审核完成',
  10: '议价审核驳回'
}

const PURCHASE_TYPE_LABELS: Record<number, string> = {
  1: '策采',
  2: '杂采'
}

const formatStatusChange = (per: unknown, cur: unknown) => {
  const a = String(per ?? '').trim()
  const b = String(cur ?? '').trim()
  if (!a && !b) return '—'
  if (!a) return `${b || '—'}`
  if (!b) return `${a} → —`
  return `${a} → ${b}`
}

export const createCrudOptions = function ({ crudExpose, context: _ctx }: CreateCrudOptionsProps): CreateCrudOptionsRet {
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
          title: '询价单号',
          type: 'text',
          search: {
            show: true,
            component: { props: { placeholder: '请输入询价单号', clearable: true } }
          },
          form: { show: false },
          column: { minWidth: 130, showOverflowTooltip: true }
        },
        buyer: {
          title: '采购负责人',
          type: 'text',
          search: {
            show: true,
            component: { props: { placeholder: '请输入采购负责人', clearable: true } }
          },
          form: { show: false },
          column: { show: false }
        },
        purchase_type: {
          title: '采购类别',
          type: 'text',
          search: { show: false },
          form: { show: false },
          column: {
            width: 88,
            formatter: ({ row }: { row: any }) => {
              const n = Number(row?.purchase_type)
              return PURCHASE_TYPE_LABELS[n] ?? (row?.purchase_type != null ? String(row.purchase_type) : '—')
            }
          }
        },
        operation_time: {
          title: '操作时间',
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
          title: '操作类型',
          type: 'text',
          search: { show: false },
          form: { show: false },
          column: {
            width: 130,
            showOverflowTooltip: true,
            formatter: ({ row }: { row: any }) => {
              const n = Number(row?.operation_type)
              if (!Number.isFinite(n) || n <= 0) return '—'
              return OPERATION_TYPE_LABELS[n] || `类型${n}`
            }
          }
        },
        operation_user: {
          title: '操作人',
          type: 'text',
          search: { show: false },
          form: { show: false },
          column: {
            width: 110,
            showOverflowTooltip: true,
            formatter: ({ row }: { row: any }) => {
              const s = String(row?.operation_user ?? '').trim()
              return s || '—'
            }
          }
        },
        status_change: {
          title: '状态变更',
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
          title: '操作描述',
          type: 'text',
          search: { show: false },
          form: { show: false },
          column: { minWidth: 180, showOverflowTooltip: true }
        },
        quotation_no: {
          title: '报价单号',
          type: 'text',
          search: { show: false },
          form: { show: false },
          column: {
            width: 116,
            showOverflowTooltip: true,
            formatter: ({ row }: { row: any }) => {
              const q = String(row?.quotation_no ?? '').trim()
              return q && q !== '-' ? q : '—'
            }
          }
        }
      }
    }
  }
}
