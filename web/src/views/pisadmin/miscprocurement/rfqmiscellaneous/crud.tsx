import { compute, dict, CreateCrudOptionsProps, CreateCrudOptionsRet } from '@fast-crud/fast-crud'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as api from './api'

const statusDict = [
  { value: 1, label: '开立' },
  { value: 2, label: '确认' },
  { value: 3, label: '发布' },
  { value: 4, label: '报价中' },
  { value: 5, label: '报价结束' },
  { value: 6, label: '比议价中' },
  { value: 7, label: '价格审核' },
  { value: 8, label: '核价通过(结束)' },
  { value: 9, label: '落标(结束)' },
  { value: 0, label: '作废' }
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
  /** 列表多选变化（用于后续多询价单比价等） */
  onTableSelectionChange?: (rows: any[]) => void
}

const STATUS_OPEN = 1
const STATUS_CONFIRMED = 2
const STATUS_PUBLISHED = 3

/** 询价单接口错误文案：将数据库唯一约束等转为可读提示 */
export const formatRfqApiErrorMessage = (err: any, fallback: string) => {
  const d = err?.response?.data
  const pick = () => {
    if (typeof d?.msg === 'string' && d.msg.trim()) return d.msg
    if (typeof d?.message === 'string' && d.message.trim()) return d.message
    if (typeof d?.detail === 'string' && d.detail.trim()) return d.detail
    if (Array.isArray(d?.non_field_errors) && d.non_field_errors.length) return String(d.non_field_errors[0])
    return ''
  }
  const raw = pick() || (typeof err?.msg === 'string' ? err.msg : '') || (typeof err?.message === 'string' ? err.message : '')
  const s = typeof raw === 'string' ? raw : String(raw)
  if (
    /重复键违反唯一约束|unique constraint|UniqueViolation|duplicate key|already exists|pis_proc_inquiry_supplie/i.test(
      s
    )
  ) {
    if (/supplier|suppli|PartId|part_id|inquiry_no/i.test(s)) {
      return '供应商名单重复：同一询价单、同一料号下不能添加相同供应商，请删除重复行或更换供应商后再保存'
    }
    return '保存失败：存在与数据库冲突的重复数据，请检查供应商名单或其它唯一项'
  }
  if (s) return s.length > 280 ? `${s.slice(0, 280)}…` : s
  return fallback
}

const getRowStatus = (row: any) => Number(row?.status)
const isOpenStatus = (row: any) => getRowStatus(row) === STATUS_OPEN
const isConfirmedStatus = (row: any) => getRowStatus(row) === STATUS_CONFIRMED
const canPublishStatus = (row: any) => isConfirmedStatus(row)
const getErrorMessage = (err: any, fallback: string) => formatRfqApiErrorMessage(err, fallback)

/** 列表行含 `suppliers` 时可先做提示；未返回嵌套时交由接口校验 */
const rowHasSuppliersList = (row: any): boolean | null => {
  const list = row?.suppliers
  if (!Array.isArray(list)) return null
  return list.length > 0
}

/** 成本模板版本号两位展示（与 pricetemplate 一致） */
export const formatCostTemplateVersionTwoDigits = (v: unknown) => {
  if (v == null || v === '') return '00'
  const n = Number(v)
  if (!Number.isFinite(n)) return String(v)
  return String(Math.trunc(n)).padStart(2, '0')
}

export const createCrudOptions = function ({
  context,
  crudExpose,
  onAdd,
  onEdit,
  onView,
  onTableSelectionChange
}: Partial<CreateCrudOptionsProps> & ExtraHooks): CreateCrudOptionsRet {
  void context
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
        delRequest: async ({ row }) => {
          try {
            return await api.DelObj(row.id)
          } catch (err: any) {
            ElMessage.error(getErrorMessage(err, '删除失败'))
            throw err
          }
        }
      },
      table: {
        rowKey: 'id',
        onSelectionChange: (changed: any[]) => {
          onTableSelectionChange?.(changed || [])
        }
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
        width: 420,
        buttons: {
          view: { show: false },
          edit: { show: false },
          remove: {
            text: '删除',
            // 禁用时不沿用 danger 的淡红底，改为 info 灰底 + disabled
            type: compute(({ row }) => (isOpenStatus(row) ? 'danger' : 'info')),
            order: 1,
            show: true,
            disabled: compute(({ row }) => !isOpenStatus(row))
          },
          customView: {
            text: '查看',
            type: 'default',
            order: 0,
            show: true,
            click({ row }) {
              onView && onView(row)
            }
          },
          customEdit: {
            text: '编辑',
            type: compute(({ row }) => (isOpenStatus(row) ? 'primary' : 'info')),
            order: 1.5,
            show: true,
            disabled: compute(({ row }) => !isOpenStatus(row)),
            click({ row }) {
              if (!isOpenStatus(row)) return
              onEdit && onEdit(row)
            }
          },
          confirm: {
            text: '确认',
            type: compute(({ row }) => (isOpenStatus(row) ? 'success' : 'info')),
            order: 2,
            show: true,
            disabled: compute(({ row }) => !isOpenStatus(row)),
            async click({ row }) {
              if (!isOpenStatus(row)) return
              try {
                const supplierOk = rowHasSuppliersList(row)
                if (supplierOk === false) {
                  ElMessage.warning('请先维护询价单供应商名单后再确认')
                  return
                }
                await ElMessageBox.confirm('确认后，该询价单将锁定并不可再编辑。如需修改，后续需执行【还原】操作', '提示', {
                  type: 'warning',
                  confirmButtonText: '确定',
                  cancelButtonText: '取消'
                })
                const res = await api.ConfirmObj(row.id)
                crudExpose?.doRefresh?.()
                return res
              } catch (err: any) {
                if (err === 'cancel' || err === 'close') return
                ElMessage.error(getErrorMessage(err, '确认失败'))
                throw err
              }
            }
          },
          restore: {
            text: '还原',
            type: compute(({ row }) => (isConfirmedStatus(row) ? 'primary' : 'info')),
            order: 2.5,
            show: true,
            disabled: compute(({ row }) => !isConfirmedStatus(row)),
            async click({ row }) {
              if (!isConfirmedStatus(row)) return
              try {
                await ElMessageBox.confirm('确认将状态还原为【开立】？', '提示', {
                  type: 'warning',
                  confirmButtonText: '确定',
                  cancelButtonText: '取消'
                })
                const res = await api.RestoreObj(row.id)
                crudExpose?.doRefresh?.()
                return res
              } catch (err: any) {
                if (err === 'cancel' || err === 'close') return
                ElMessage.error(getErrorMessage(err, '还原失败'))
                throw err
              }
            }
          },
          publish: {
            text: '发布',
            type: compute(({ row }) => (canPublishStatus(row) ? 'warning' : 'info')),
            order: 3,
            show: true,
            disabled: compute(({ row }) => !canPublishStatus(row)),
            async click({ row }) {
              if (!canPublishStatus(row)) return
              try {
                await ElMessageBox.confirm('确认将状态改为【发布】？', '提示', {
                  type: 'warning',
                  confirmButtonText: '确定',
                  cancelButtonText: '取消'
                })
                const res = await api.PublishObj(row.id)
                crudExpose?.doRefresh?.()
                return res
              } catch (err: any) {
                if (err === 'cancel' || err === 'close') return
                ElMessage.error(getErrorMessage(err, '发布失败'))
                throw err
              }
            }
          }
        }
      },
      columns: {
        $checked: {
          title: '',
          form: { show: false },
          search: { show: false },
          column: {
            type: 'selection',
            align: 'center',
            width: 52,
            fixed: 'left',
            columnSetDisabled: true
          }
        },
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
          column: {
            minWidth: 180,
            showOverflowTooltip: true,
            formatter: ({ row, value }: { row: any; value: unknown }) => {
              const code = String(value ?? row?.template ?? row?.template_code ?? '').trim()
              const verRaw = row?.template_version ?? row?.templateVersion ?? row?.cost_template_version
              if (!code) return ''
              if (verRaw != null && verRaw !== '') return `${code}（V${formatCostTemplateVersionTwoDigits(verRaw)}）`
              return code
            }
          }
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
          column: { width: 140 }
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
