import { dict, CreateCrudOptionsProps, CreateCrudOptionsRet } from '@fast-crud/fast-crud'
import * as api from './api'
import { GetCompanies } from '../currency/api'
import { GetList as GetUnits } from '../unit/api'
import { ElMessage } from 'element-plus'

const statusDict = [
  { value: 1, label: '可用' },
  { value: 0, label: '不可用' }
]

const stationTypeDict = [
  { value: 1, label: '模治具' },
  { value: 2, label: '石墨' }
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

const loadUnitOptions = async () => {
  try {
    const res = await GetUnits({ page: 1, page_size: 1000, pageSize: 1000 })
    const list =
      res?.data?.data?.results ||
      res?.data?.results ||
      res?.data?.list ||
      res?.data ||
      res?.results ||
      res?.list ||
      []
    return (Array.isArray(list) ? list : []).map((u: any) => ({
      value: u.unitcode || u.unit_code || u.unit || u.code,
      label: u.unitname || u.unit_name || u.unit || u.code
    }))
  } catch (e) {
    console.warn('加载计量单位失败', e)
    return []
  }
}

// 预取一次，进入页面即触发
void loadCompanyOptions()

export const createCrudOptions = function ({ crudExpose }: CreateCrudOptionsProps): CreateCrudOptionsRet {
  void crudExpose

  const ensureStationCodeUnique = async (companyCode: string, stationCode: string, currentId?: number) => {
    if (!companyCode || !stationCode) return
    const res = await api.GetList({ company_code: companyCode, stationcode: stationCode, page: 1, page_size: 1, pageSize: 1 })
    const list =
      res?.data?.data?.results ||
      res?.data?.results ||
      res?.data?.list ||
      res?.data ||
      res?.results ||
      res?.list ||
      []
    const exists = Array.isArray(list)
      ? list.find((item: any) => item.company_code === companyCode && item.stationcode === stationCode)
      : null
    if (exists && (!currentId || exists.id !== currentId)) {
      throw new Error('同一交易厂区下工站代码已存在，不可重复')
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
            await ensureStationCodeUnique(form.company_code, form.stationcode)
            return await api.AddObj(form)
          } catch (err: any) {
            ElMessage.error(err?.message || '保存失败')
            throw err
          }
        },
        editRequest: async ({ form, row }) => {
          try {
            await ensureStationCodeUnique(form.company_code, form.stationcode, row.id)
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
          column: { minWidth: 160, showOverflowTooltip: true }
        },
        stationcode: {
          title: '工站代码',
          type: 'input',
          search: { show: true, component: { props: { placeholder: '请输入工站代码', clearable: true } } },
          form: { rules: [{ required: true, message: '请输入工站代码' }] },
          column: { minWidth: 140, showOverflowTooltip: true }
        },
        stationname: {
          title: '工站名称',
          type: 'input',
          search: { show: true, component: { props: { placeholder: '请输入工站名称', clearable: true } } },
          form: { rules: [{ required: true, message: '请输入工站名称' }] },
          column: { minWidth: 160, showOverflowTooltip: true }
        },        
        stationtype: {
          title: '工站类型',
          type: 'dict-select',
          dict: dict({ data: stationTypeDict }),
          form: { rules: [{ required: true, message: '请选择工站类型' }] },
          column: { width: 140, showOverflowTooltip: true }
        },
        unit: {
          title: '计量单位',
          type: 'dict-select',
          dict: dict({
            cache: false,
            getData: async () => loadUnitOptions()
          }),
          form: { rules: [{ required: true, message: '请选择计量单位' }] },
          column: { width: 140, showOverflowTooltip: true }
        },
        rate: {
          title: '费率',
          type: 'number',
          form: { rules: [{ required: true, message: '请输入费率' }], component: { props: { precision: 2 } } },
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
