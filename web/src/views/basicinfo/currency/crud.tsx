import { dict, CreateCrudOptionsProps, CreateCrudOptionsRet } from '@fast-crud/fast-crud'
import * as api from './api'

const statusDict = [
  { value: 1, label: '可用' },
  { value: 0, label: '不可用' }
]

const loadCompanyOptions = async () => {
  try {
    const res = await api.GetCompanies({ page: 1, page_size: 1000, pageSize: 1000 })
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

// 预取一次，确保进入页面时就触发请求
void loadCompanyOptions()

export const createCrudOptions = function ({ crudExpose }: CreateCrudOptionsProps): CreateCrudOptionsRet {
  void crudExpose
  return {
    crudOptions: {
      form: {
        labelWidth: '110px'
      },
      request: {
        pageRequest: async (query) => api.GetList(query),
        addRequest: async ({ form }) => api.AddObj(form),
        editRequest: async ({ form, row }) => api.UpdateObj({ ...form, id: row.id }),
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
        currencyname: {
          title: '货币名称',
          type: 'input',
          search: { show: true, component: { props: { placeholder: '请输入货币名称', clearable: true } } },
          form: { rules: [{ required: true, message: '请输入货币名称' }] },
          column: { minWidth: 160, showOverflowTooltip: true }
        },
        currencycode: {
          title: '货币代码',
          type: 'input',
          search: { show: true, component: { props: { placeholder: '请输入货币代码', clearable: true } } },
          column: { minWidth: 140, showOverflowTooltip: true }
        },
        currencysymbol: {
          title: '货币符号',
          type: 'input',
          form: { rules: [{ required: true, message: '请输入货币符号' }] },
          column: { width: 120, showOverflowTooltip: true }
        },
        factory: {
          title: '交易厂区',
          type: 'dict-select',
          dict: dict({
            cache: false,
            value: 'company_code',
            label: 'company_short_name',
            getData: async () => {
              return loadCompanyOptions()
            }
          }),
          search: { show: true },
          column: { width: 160, showOverflowTooltip: true }
        },
        tax: {
          title: '税率(%)',
          type: 'number',
          form: { rules: [{ required: true, message: '请输入税率' }], component: { props: { precision: 2 } } },
          column: { width: 120 }
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
