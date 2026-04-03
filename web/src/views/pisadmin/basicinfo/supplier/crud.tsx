import { dict, CreateCrudOptionsProps, CreateCrudOptionsRet } from '@fast-crud/fast-crud'
import * as api from './api'
import { GetCompanies } from '../currency/api'
import { GetList as GetCurrencies } from '../currency/api'
import { ElMessage } from 'element-plus'

const statusDict = [
  { value: 1, label: '可用' },
  { value: 0, label: '不可用' }
]

const vendorTypeDict = [
  { value: '国有', label: '国有' },
  { value: '集体', label: '集体' },
  { value: '私营', label: '私营' },
  { value: '合资', label: '合资' },
  { value: '独资', label: '独资' },
  { value: '其他', label: '其他' }
]

const paymentTermDict = [
  { value: 'tt_30_70', label: 'T/T 30%预付，70%出货前' },
  { value: 'net30', label: '月结30天' },
  { value: 'net45', label: '月结45天' },
  { value: 'prepaid', label: '全额预付' }
]

const incotermDict = [
  { value: 'EXW', label: 'EXW（工厂交货）' },
  { value: 'FCA', label: 'FCA（货交承运人）' },
  { value: 'CPT', label: 'CPT（运费付至）' },
  { value: 'CIP', label: 'CIP（运费及保险费付至）' },
  { value: 'DAP', label: 'DAP（目的地交货）' },
  { value: 'DPU', label: 'DPU（卸货地交货）' },
  { value: 'DDP', label: 'DDP（完税后交货）' },
  { value: 'FAS', label: 'FAS（船边交货）' },
  { value: 'FOB', label: 'FOB（船上交货）' },
  { value: 'CFR', label: 'CFR（成本加运费）' },
  { value: 'CIF', label: 'CIF（成本、保险费加运费）' }
]

const loadCompanyOptions = async () => {
  try {
    const res = await GetCompanies({ page: 1, page_size: 1000, pageSize: 1000 })
    const list =
      res?.data?.data?.results ||
      res?.data?.results ||
      res?.data?.list ||
      res?.data ||
      res?.results ||
      res?.list ||
      []
    return (Array.isArray(list) ? list : []).map((c: any) => ({
      company_code: c.company_code,
      company_short_name: c.company_short_name || c.company_code || c.company_name
    }))
  } catch (e) {
    console.warn('加载公司列表失败', e)
    return []
  }
}

const loadCurrencyOptions = async (companyCode?: string) => {
  try {
    const params: any = { page: 1, page_size: 500, pageSize: 500 }
    if (companyCode) params.factory = companyCode
    const res = await GetCurrencies(params)
    const list =
      res?.data?.data?.results ||
      res?.data?.results ||
      res?.data?.list ||
      res?.data ||
      res?.results ||
      res?.list ||
      []
    return (Array.isArray(list) ? list : []).map((c: any) => ({
      value: c.currencycode || c.currency_code,
      label: c.currencyname || c.currency_code || c.currencycode || c.currency_name
    }))
  } catch (e) {
    console.warn('加载币别列表失败', e)
    return []
  }
}

// 预取一次公司列表
void loadCompanyOptions()

export const createCrudOptions = function ({ crudExpose }: CreateCrudOptionsProps): CreateCrudOptionsRet {
  void crudExpose

  const ensureSupplierUnique = async (companyCode: string, supplierId: string, currentId?: number) => {
    if (!companyCode || !supplierId) return
    const res = await api.GetList({ company_code: companyCode, supplier_id: supplierId, page: 1, page_size: 1, pageSize: 1 })
    const list =
      res?.data?.data?.results ||
      res?.data?.results ||
      res?.data?.list ||
      res?.data ||
      res?.results ||
      res?.list ||
      []
    const exists = Array.isArray(list)
      ? list.find((item: any) => item.company_code === companyCode && item.supplier_id === supplierId)
      : null
    if (exists && (!currentId || exists.id !== currentId)) {
      throw new Error('同一交易厂区下供应商代码已存在，不可重复')
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
            await ensureSupplierUnique(form.company_code, form.supplier_id)
            return await api.AddObj(form)
          } catch (err: any) {
            ElMessage.error(err?.message || '保存失败')
            throw err
          }
        },
        editRequest: async ({ form, row }) => {
          try {
            await ensureSupplierUnique(form.company_code, form.supplier_id, row.id)
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
        company_code: {
          title: '交易厂区',
          type: 'dict-select',
          dict: dict({
            cache: false,
            value: 'company_code',
            label: 'company_short_name',
            getData: async () => loadCompanyOptions()
          }),
          search: { show: true },
          form: {
            rules: [{ required: true, message: '请选择交易厂区' }],
            component: {
              on: {
                change({ form, value }: any) {
                  // 切换厂区时清空币别，触发重新加载
                  form.transaction_currency = undefined
                  form.company_code = value
                }
              }
            }
          },
          column: { minWidth: 160, showOverflowTooltip: true }
        },
        supplier_id: {
          title: '供应商代码/ID',
          type: 'input',
          search: { show: true, component: { props: { placeholder: '请输入供应商代码/ID', clearable: true } } },
          form: { rules: [{ required: true, message: '请输入供应商代码/ID' }] },
          column: { minWidth: 140, showOverflowTooltip: true }
        },
        supplier_name: {
          title: '供应商全称',
          type: 'input',
          search: { show: true, component: { props: { placeholder: '请输入供应商全称', clearable: true } } },
          form: { rules: [{ required: true, message: '请输入供应商全称' }] },
          column: { minWidth: 180, showOverflowTooltip: true }
        },
        supplier_short_name: {
          title: '供应商简称',
          type: 'input',
          form: { rules: [{ required: true, message: '请输入供应商简称' }] },
          column: { minWidth: 160, showOverflowTooltip: true }
        },
        vendor_type: {
          title: '厂商性质',
          type: 'dict-select',
          dict: dict({ data: vendorTypeDict }),
          column: { minWidth: 140, showOverflowTooltip: true }
        },
        payment_terms: {
          title: '付款条件',
          type: 'dict-select',
          dict: dict({ data: paymentTermDict }),
          column: { minWidth: 160, showOverflowTooltip: true }
        },
        transaction_currency: {
          title: '交易货币',
          type: 'dict-select',
          dict: dict({
            cache: false,
            getData: async ({ form }: any = {}) => {
              return loadCurrencyOptions(form?.company_code)
            }
          }),
          form: { placeholder: '先选择交易厂区' },
          column: { minWidth: 140, showOverflowTooltip: true }
        },
        incoterms: {
          title: '国际条款',
          type: 'dict-select',
          dict: dict({ data: incotermDict }),
          column: { minWidth: 160, showOverflowTooltip: true }
        },
        supplier_level: {
          title: '供应商等级',
          type: 'input',
          column: { minWidth: 120, showOverflowTooltip: true }
        },
        contact_person: {
          title: '联络人',
          type: 'input',
          form: { rules: [{ required: true, message: '请输入联络人' }] },
          column: { minWidth: 120, showOverflowTooltip: true }
        },
        contact_phone: {
          title: '联络人电话',
          type: 'input',
          form: { rules: [{ required: true, message: '请输入联络人电话' }] },
          column: { minWidth: 140, showOverflowTooltip: true }
        },
        contact_email: {
          title: '联络人邮箱',
          type: 'input',
          form: { rules: [{ required: true, message: '请输入联络人邮箱' }] },
          column: { minWidth: 180, showOverflowTooltip: true }
        },
        country: {
          title: '国家',
          type: 'input',
          form: { rules: [{ required: true, message: '请输入国家' }] },
          column: { minWidth: 120, showOverflowTooltip: true }
        },
        province: {
          title: '省州',
          type: 'input',
          form: { rules: [{ required: true, message: '请输入省州' }] },
          column: { minWidth: 120, showOverflowTooltip: true }
        },
        city: {
          title: '城市',
          type: 'input',
          column: { minWidth: 120, showOverflowTooltip: true }
        },
        address: {
          title: '详细地址',
          type: 'textarea',
          column: { minWidth: 200, showOverflowTooltip: true },
          form: { component: { props: { rows: 2 } } }
        },
        postal_code: {
          title: '邮递区号',
          type: 'input',
          column: { minWidth: 120, showOverflowTooltip: true }
        },
        status: {
          title: '可用状态',
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
