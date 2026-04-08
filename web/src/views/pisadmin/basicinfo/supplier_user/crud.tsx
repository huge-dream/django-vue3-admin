import { dict, CreateCrudOptionsProps, CreateCrudOptionsRet } from '@fast-crud/fast-crud'
import * as api from './api'
import { GetList as GetSupplierList } from '../supplier/api'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'

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
  const { t } = useI18n()

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
      throw new Error(t('message.pages.basicinfo.supplierUser.userEmail') + t('message.pages.menu.validation.alreadyExists'))
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
            const res = await api.AddObj(form)
            ElMessage.success(
              '保存成功，已同步创建系统用户（登录账号为联络人邮箱，初始密码为系统默认密码，部门：供应商）'
            )
            return res
          } catch (err: any) {
            ElMessage.error(err?.msg || err?.message || '保存失败')
            throw err
          }
        },
        editRequest: async ({ form, row }) => {
          try {
            await ensureUserEmailUnique(form.supplier_id, form.user_email, row.id)
            return await api.UpdateObj({ ...form, id: row.id })
          } catch (err: any) {
            ElMessage.error(err?.msg || err?.message || '保存失败')
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
          title: t('message.pages.basicinfo.supplierUser.supplierId'),
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
          search: { show: true, component: { props: { placeholder: t('message.pages.basicinfo.emailnotice.selectOrSearch'), filterable: true, clearable: true } } },
          form: {
            rules: [{ required: true, message: t('message.pages.basicinfo.supplierUser.supplierId') + ' ' + t('message.pages.menu.validation.fieldNameRequired') }],
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
          title: t('message.pages.basicinfo.supplierUser.supplierName'),
          type: 'input',
          search: { show: true, component: { props: { placeholder: t('message.pages.basicinfo.supplierUser.supplierName'), clearable: true } } },
          form: {
            rules: [{ required: true, message: '请先选择供应商唯一ID，将自动带出供应商全称' }],
            component: {
              props: {
                disabled: true,
                placeholder: t('message.pages.basicinfo.supplierUser.autoFillNote')
              }
            }
          },
          column: { minWidth: 180, showOverflowTooltip: true }
        },
        supplier_role: {
          title: t('message.pages.basicinfo.supplierUser.supplierRole'),
          type: 'dict-select',
          dict: dict({ data: [{ value: 1, label: t('message.pages.basicinfo.supplierUser.roleQuote') }] }),
          search: { show: true },
          form: {
            rules: [{ required: true, message: t('message.pages.basicinfo.supplierUser.supplierRole') + ' ' + t('message.pages.menu.validation.fieldNameRequired') }],
            value: 1
          },
          column: { minWidth: 120, showOverflowTooltip: true }
        },
        user_email: {
          title: t('message.pages.basicinfo.supplierUser.userEmail'),
          type: 'input',
          search: { show: true, component: { props: { placeholder: t('message.pages.basicinfo.supplierUser.userEmail'), clearable: true } } },
          form: { rules: [{ required: true, message: t('message.pages.basicinfo.supplierUser.userEmail') + ' ' + t('message.pages.menu.validation.fieldNameRequired') }] },
          column: { minWidth: 200, showOverflowTooltip: true }
        },
        user_name: {
          title: t('message.pages.basicinfo.supplierUser.userName'),
          type: 'input',
          search: { show: true, component: { props: { placeholder: t('message.pages.basicinfo.supplierUser.userName'), clearable: true } } },
          form: { rules: [{ required: true, message: t('message.pages.basicinfo.supplierUser.userName') + ' ' + t('message.pages.menu.validation.fieldNameRequired') }] },
          column: { minWidth: 120, showOverflowTooltip: true }
        },
        user_phone: {
          title: t('message.pages.basicinfo.supplierUser.userPhone'),
          type: 'input',
          search: { show: true, component: { props: { placeholder: t('message.pages.basicinfo.supplierUser.userPhone'), clearable: true } } },
          form: { rules: [{ required: true, message: t('message.pages.basicinfo.supplierUser.userPhone') + ' ' + t('message.pages.menu.validation.fieldNameRequired') }] },
          column: { minWidth: 140, showOverflowTooltip: true }
        },
        status: {
          title: t('message.pages.basicinfo.supplierUser.status'),
          type: 'dict-switch',
          dict: dict({ data: [{ value: 1, label: t('message.pages.basicinfo.supplierUser.statusValid') }, { value: 0, label: t('message.pages.basicinfo.supplierUser.statusInvalid') }] }),
          form: { value: 1 },
          column: { width: 120 }
        },
        create_datetime: {
          title: t('message.pages.basicinfo.supplierUser.createTime'),
          type: 'datetime',
          form: { show: false },
          column: { width: 180 }
        },
        update_datetime: {
          title: t('message.pages.basicinfo.supplierUser.updateTime'),
          type: 'datetime',
          form: { show: false },
          column: { width: 180 }
        }
      }
    }
  }
}
