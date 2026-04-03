import { dict, CreateCrudOptionsProps, CreateCrudOptionsRet } from '@fast-crud/fast-crud'
import * as api from './api'
import { GetList as GetSupplierList } from '../supplier/api'
import { ElMessage } from 'element-plus'

const statusDict = [
  { value: 1, label: '有效' },
  { value: 0, label: '无效' }
]

const supplierRoleDict = [{ value: 1, label: '报价' }]

let supplierById: Record<string, any> = {}

/** 兼容 dvadmin 分页：{ code, data: [...] }；部分封装可能是 data.results */
const extractSupplierList = (res: any) => {
  const inner = res?.data
  if (Array.isArray(inner)) return inner
  if (Array.isArray(inner?.results)) return inner.results
  if (Array.isArray(inner?.data)) return inner.data
  if (Array.isArray(inner?.list)) return inner.list
  const flat =
    res?.data?.data?.results ||
    res?.data?.results ||
    res?.data?.list ||
    res?.results ||
    res?.list ||
    []
  return Array.isArray(flat) ? flat : []
}

const loadSupplierOptions = async () => {
  try {
    const res = await GetSupplierList({ page: 1, page_size: 1000, pageSize: 1000 })
    const arr = extractSupplierList(res)
    supplierById = Object.fromEntries(arr.map((s: any) => [String(s.supplier_id), s]))
    return arr
  } catch (e) {
    console.warn('加载供应商列表失败', e)
    supplierById = {}
    return []
  }
}

/** 按供应商唯一ID 从「供应商信息」接口取一条（与询价单选料号带出名称类似：先选项缓存，必要时再查接口） */
const fetchSupplierBySupplierId = async (supplierId: string) => {
  if (!supplierId) return null
  try {
    const res = await GetSupplierList({
      supplier_id: supplierId,
      page: 1,
      page_size: 5,
      pageSize: 5
    })
    const arr = extractSupplierList(res)
    const row = arr.find((s: any) => String(s.supplier_id) === String(supplierId)) || arr[0] || null
    if (row) supplierById[String(supplierId)] = row
    return row
  } catch (e) {
    console.warn('按供应商ID查询供应商信息失败', e)
    return null
  }
}

void loadSupplierOptions()

export const createCrudOptions = function ({ crudExpose }: CreateCrudOptionsProps): CreateCrudOptionsRet {
  void crudExpose

  const ensureUserEmailUnique = async (supplierId: string, userEmail: string, currentId?: number) => {
    if (!supplierId || !userEmail) return
    const res = await api.GetList({
      supplier_id: supplierId,
      user_email: userEmail,
      page: 1,
      page_size: 50,
      pageSize: 50
    })
    const list = extractSupplierList(res)
    const exists = Array.isArray(list)
      ? list.find(
          (item: any) =>
            String(item.supplier_id) === String(supplierId) &&
            String(item.user_email || '').trim().toLowerCase() === String(userEmail).trim().toLowerCase()
        )
      : null
    if (exists && (!currentId || exists.id !== currentId)) {
      throw new Error('同一供应商下该联络邮箱已存在')
    }
  }

  return {
    crudOptions: {
      form: {
        labelWidth: '110px'
      },
      request: {
        pageRequest: async (query) => api.GetList(query),
        addRequest: async ({ form }) => {
          try {
            await ensureUserEmailUnique(form.supplier_id, form.user_email)
            return await api.AddObj(form)
          } catch (err: any) {
            ElMessage.error(err?.message || '保存失败')
            throw err
          }
        },
        editRequest: async ({ form, row }) => {
          try {
            await ensureUserEmailUnique(form.supplier_id, form.user_email, row.id)
            return await api.UpdateObj({ ...form, id: row.id })
          } catch (err: any) {
            ElMessage.error(err?.message || '保存失败')
            throw err
          }
        },
        delRequest: async ({ row }) => api.DelObj(row.id)
      },
      table: {
        rowKey: 'id'
      },
      actionbar: {
        buttons: {
          add: { show: true }
        }
      },
      rowHandle: {
        fixed: 'right'
      },
      columns: {
        supplier_id: {
          title: '供应商唯一ID',
          type: 'dict-select',
          dict: dict({
            cache: false,
            value: 'supplier_id',
            label: 'supplier_short_name',
            getData: async () => {
              const rows = await loadSupplierOptions()
              return rows.map((s: any) => ({
                ...s,
                supplier_short_name: `${s.supplier_short_name || s.supplier_name || ''} (${s.supplier_id})`
              }))
            }
          }),
          search: { show: true, component: { props: { placeholder: '请选择或搜索', filterable: true, clearable: true } } },
          form: {
            rules: [{ required: true, message: '请选择供应商' }],
            /** dict-select 需用 fast-crud 的 valueChange；component.on.change 往往不会触发 */
            valueChange: async ({ value, form }: any) => {
              const v = value
              if (v == null || v === '') {
                form.supplier_name = ''
                return
              }
              let s = supplierById[String(v)]
              if (!s?.supplier_name) {
                await loadSupplierOptions()
                s = supplierById[String(v)]
              }
              if (!s?.supplier_name) {
                s = await fetchSupplierBySupplierId(String(v))
              }
              form.supplier_name = s?.supplier_name != null ? String(s.supplier_name) : ''
            },
            component: {
              props: { filterable: true }
            }
          },
          editForm: {
            component: {
              props: {
                disabled: true
              }
            }
          },
          column: { minWidth: 200, showOverflowTooltip: true }
        },
        supplier_name: {
          title: '供应商全称',
          type: 'input',
          search: { show: true, component: { props: { placeholder: '请输入供应商全称', clearable: true } } },
          form: {
            rules: [{ required: true, message: '请先选择供应商唯一ID，将自动带出供应商全称' }],
            component: {
              props: {
                disabled: true,
                placeholder: '选择供应商唯一ID后自动带出'
              }
            }
          },
          column: { minWidth: 180, showOverflowTooltip: true }
        },
        supplier_role: {
          title: '供应商角色',
          type: 'dict-select',
          dict: dict({ data: supplierRoleDict }),
          search: { show: true },
          form: {
            rules: [{ required: true, message: '请选择供应商角色' }],
            value: 1
          },
          column: { minWidth: 120, showOverflowTooltip: true }
        },
        user_email: {
          title: '联络人邮箱',
          type: 'input',
          search: { show: true, component: { props: { placeholder: '请输入邮箱', clearable: true } } },
          form: { rules: [{ required: true, message: '请输入联络人邮箱' }] },
          column: { minWidth: 200, showOverflowTooltip: true }
        },
        user_name: {
          title: '联络人',
          type: 'input',
          search: { show: true, component: { props: { placeholder: '请输入联络人', clearable: true } } },
          form: { rules: [{ required: true, message: '请输入联络人' }] },
          column: { minWidth: 120, showOverflowTooltip: true }
        },
        user_phone: {
          title: '联络人电话',
          type: 'input',
          search: { show: true, component: { props: { placeholder: '请输入电话', clearable: true } } },
          form: { rules: [{ required: true, message: '请输入联络人电话' }] },
          column: { minWidth: 140, showOverflowTooltip: true }
        },
        status: {
          title: '有效否',
          type: 'dict-switch',
          dict: dict({ data: statusDict }),
          form: { value: 1 },
          column: { width: 120 }
        },
        create_datetime: {
          title: '创建时间',
          type: 'datetime',
          form: { show: false },
          column: { width: 180 }
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
