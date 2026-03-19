import { dict, CreateCrudOptionsProps, CreateCrudOptionsRet } from '@fast-crud/fast-crud'
import * as api from './api'

const statusDict = [
  { value: 1, label: '草稿' },
  { value: 2, label: '已确认' },
  { value: 3, label: '已发布' },
  { value: 4, label: '询价中' },
  { value: 5, label: '议价中' },
  { value: 6, label: '已议价' },
  { value: 7, label: '价格评审' },
  { value: 8, label: '作废' },
  { value: 9, label: '新增(结束)' }
]

const paymentMethods = [
  { value: 1, label: '月结30天' },
  { value: 2, label: '月结60天' },
  { value: 3, label: '不到付款' },
  { value: 4, label: '预付30%' },
  { value: 5, label: '预付50%' },
  { value: 6, label: '余款至生产' },
  { value: 7, label: '价格审核' },
  { value: 8, label: '价格结算(运费)' },
  { value: 9, label: '新建(结束)' }
]

const formatQuoteDeadlineDisplay = (value: unknown) => {
  if (!value) return ''
  const text = String(value).trim()
  if (!text) return ''
  const matched = text.match(/^(\d{4}-\d{2}-\d{2})[ T](\d{2})/)
  if (matched) {
    return `${matched[1]} ${matched[2]}:00`
  }
  const dateOnly = text.match(/^(\d{4}-\d{2}-\d{2})$/)
  if (dateOnly) {
    return `${dateOnly[1]} 00:00`
  }
  return text
}

const normalizeList = (value: unknown, label: string) => {
  if (value === null || value === undefined || value === '') return []
  if (typeof value === 'string') {
    const parsed = JSON.parse(value)
    if (!Array.isArray(parsed)) throw new Error(`${label} 需为 JSON 数组`)
    return parsed
  }
  if (Array.isArray(value)) return value
  throw new Error(`${label} 需为 JSON 数组`)
}

export const normalizeDict = (value: unknown, label: string) => {
  if (value === null || value === undefined || value === '') return {}
  if (typeof value === 'string') {
    const parsed = JSON.parse(value)
    if (parsed === null || typeof parsed !== 'object' || Array.isArray(parsed)) {
      throw new Error(`${label} 需为 JSON 对象`)
    }
    return parsed
  }
  if (typeof value === 'object') return value as Record<string, unknown>
  throw new Error(`${label} 需为 JSON 对象`)
}

type ExtraHooks = {
  onAdd?: () => void
  onEdit?: (row: any) => void
  onView?: (row: any) => void
}

export const createCrudOptions = function ({ context, crudExpose, onAdd, onEdit, onView }: Partial<CreateCrudOptionsProps> & ExtraHooks): CreateCrudOptionsRet {
  void context
  void crudExpose
  return {
    crudOptions: {
      form: {
        labelWidth: '120px',
        col: { span: 12 },
        wrapper: { is: 'el-dialog', width: '960px', top: '6vh', title: '询价单' },
        group: {
          type: 'tab',
          base: { label: '基础信息', columns: ['code', 'title', 'product_category', 'template', 'part_no', 'part_name', 'quote_deadline', 'purchase_qty', 'buyer', 'currency', 'plant', 'target_price', 'lead_time_days', 'payment_term', 'status', 'remark'] },
          cost: { label: '成本结构', columns: ['cost_items'] },
          vendors: { label: '供应商名单', columns: ['vendors'] },
          attachments: { label: '附件', columns: ['attachments'] }
        }
      },
      request: {
        pageRequest: async (query) => api.GetList(query),
        // 新版：新增/编辑由 index.vue 自定义弹窗负责（嵌套子表一次提交）
        addRequest: async ({ form }) => api.AddObj(form),
        editRequest: async ({ form, row }) => api.UpdateObj({ ...form, id: row.id }),
        delRequest: async ({ row }) => api.DelObj(row.id)
      },
      table: {
        rowKey: 'id'
      },
      actionbar: {
        buttons: {
          add: {
            show: true,
            text: '新建询价单',
            click() {
              onAdd && onAdd()
            }
          }
        }
      },
      rowHandle: {
        fixed: 'right',
        width: 380,
        buttons: {
          view: { show: false },
          edit: { show: false },
          customView: {
            text: '查看',
            type: 'info',
            order: 0,
            show: true,
            click({ row }) {
              onView && onView(row)
            }
          },
          customEdit: {
            text: '编辑',
            type: 'primary',
            show: true,
            click({ row }) {
              onEdit && onEdit(row)
            }
          },
          confirm: {
            text: '确认',
            type: 'success',
            order: 2,
            show: ((ctx: any) => ctx.row.status !== 2) as any,
            popConfirm: {
              title: '确认将状态改为【确认】？',
              confirm(ctx: any) {
                const { row } = ctx
                return api.UpdateObj({ ...row, status: 2 })
              }
            }
          },
          publish: {
            text: '发布',
            type: 'warning',
            order: 3,
            show: ((ctx: any) => ctx.row.status !== 3) as any,
            popConfirm: {
              title: '确认将状态改为【发布】？',
              confirm(ctx: any) {
                const { row } = ctx
                return api.UpdateObj({ ...row, status: 3 })
              }
            }
          }
        }
      },
      columns: {
        inquiry_no: {
          title: '询价单号',
          type: 'input',
          search: {
            show: true,
            component: { props: { placeholder: '请输入询价单号', clearable: true } }
          },
          form: {
            show: false
          },
          column: { minWidth: 140 }
        },
        title: {
          title: '询价单名称',
          type: 'input',
          search: {
            show: true,
            component: { props: { placeholder: '请输入询价单名称', clearable: true } }
          },
          form: { rules: [{ required: true, message: '请输入询价单名称' }] },
          column: { minWidth: 160, showOverflowTooltip: true }
        },
        template: {
          title: '询价模版',
          type: 'input',
          column: { minWidth: 140, showOverflowTooltip: true }
        },
        quote_deadline: {
          title: '报价截止时',
          type: 'datetime',
          column: {
            width: 160,
            formatter: ({ value }: { value: unknown }) => formatQuoteDeadlineDisplay(value)
          }
        },
        buyer: {
          title: '采购负责人',
          type: 'input',
          search: {
            show: true,
            component: { props: { placeholder: '请输入采购负责人', clearable: true } }
          },
          form: { rules: [{ required: true, message: '请输入采购负责人' }] },
          column: { minWidth: 120 }
        },
        currency: {
          title: '币别',
          type: 'dict-select',
          dict: dict({ data: [
            { value: 'CNY', label: 'CNY' },
            { value: 'USD', label: 'USD' }
          ] }),
          column: { width: 100 },
          form: { value: 'CNY' }
        },
        lead_time_days: {
          title: '交货周期(天)',
          type: 'number',
          column: { width: 120 },
          form: { component: { props: { precision: 0 } } }
        },
        payment_method: {
          title: '付款方式',
          type: 'dict-select',
          dict: dict({ data: paymentMethods }),
          column: { width: 140, showOverflowTooltip: true },
          form: { show: false }
        },
        status: {
          title: '状态',
          type: 'dict-select',
          dict: dict({ data: statusDict }),
          column: { width: 120 }
        },
        remark: {
          title: '备注',
          type: 'textarea',
          column: { minWidth: 180, showOverflowTooltip: true },
          form: { component: { props: { rows: 3 } } }
        },
        update_datetime: {
          title: '更新时间',
          type: 'datetime',
          form: { show: false },
          column: { width: 180 }
        }
      }
    }
  }
}
