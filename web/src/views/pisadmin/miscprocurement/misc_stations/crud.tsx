import { dict, CreateCrudOptionsProps, CreateCrudOptionsRet } from '@fast-crud/fast-crud'
import * as api from './api'
import { GetCompanies } from '../../basicinfo/currency/api'
import { GetList as GetUnits } from '../../basicinfo/unit/api'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'

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

void loadCompanyOptions()

export const createCrudOptions = function ({ crudExpose }: CreateCrudOptionsProps): CreateCrudOptionsRet {
  const { t } = useI18n()

  const statusDict = [
    { value: 1, label: t('message.pages.miscprocurement.stationInfo.statusEnabled') },
    { value: 0, label: t('message.pages.miscprocurement.stationInfo.statusDisabled') }
  ]

  const stationTypeDict = [
    { value: 1, label: t('message.pages.miscprocurement.stationInfo.typeTooling') },
    { value: 2, label: t('message.pages.miscprocurement.stationInfo.typeGraphite') }
  ]

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
      throw new Error(t('message.pages.miscprocurement.stationInfo.companyCode') + t('message.pages.miscprocurement.stationInfo.stationcode') + t('message.pages.menu.validation.alreadyExists'))
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
          title: t('message.pages.miscprocurement.stationInfo.companyCode'),
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
          title: t('message.pages.miscprocurement.stationInfo.stationcode'),
          type: 'input',
          search: { show: true, component: { props: { placeholder: t('message.pages.miscprocurement.stationInfo.stationcode'), clearable: true } } },
          form: { rules: [{ required: true, message: t('message.pages.miscprocurement.stationInfo.stationcode') + ' ' + t('message.pages.menu.validation.fieldNameRequired') }] },
          editForm: {
            component: { props: { disabled: true } }
          },
          column: { minWidth: 140, showOverflowTooltip: true }
        },
        stationname: {
          title: t('message.pages.miscprocurement.stationInfo.stationname'),
          type: 'input',
          search: { show: true, component: { props: { placeholder: t('message.pages.miscprocurement.stationInfo.stationname'), clearable: true } } },
          form: { rules: [{ required: true, message: t('message.pages.miscprocurement.stationInfo.stationname') + ' ' + t('message.pages.menu.validation.fieldNameRequired') }] },
          column: { minWidth: 160, showOverflowTooltip: true }
        },
        stationtype: {
          title: t('message.pages.miscprocurement.stationInfo.stationtype'),
          type: 'dict-select',
          dict: dict({ data: stationTypeDict }),
          form: { rules: [{ required: true, message: t('message.pages.miscprocurement.stationInfo.stationtype') + ' ' + t('message.pages.menu.validation.fieldNameRequired') }] },
          column: { width: 140, showOverflowTooltip: true }
        },
        unit: {
          title: t('message.pages.miscprocurement.stationInfo.unit'),
          type: 'dict-select',
          dict: dict({
            cache: false,
            getData: async () => loadUnitOptions()
          }),
          form: { rules: [{ required: true, message: t('message.pages.miscprocurement.stationInfo.unit') + ' ' + t('message.pages.menu.validation.fieldNameRequired') }] },
          column: { width: 140, showOverflowTooltip: true }
        },
        rate: {
          title: t('message.pages.miscprocurement.stationInfo.rate'),
          type: 'number',
          form: { rules: [{ required: true, message: t('message.pages.miscprocurement.stationInfo.rate') + ' ' + t('message.pages.menu.validation.fieldNameRequired') }], component: { props: { precision: 2 } } },
          column: { width: 120 }
        },
        status: {
          title: t('message.pages.miscprocurement.stationInfo.status'),
          type: 'dict-switch',
          dict: dict({ data: statusDict }),
          form: { value: 1 },
          column: { width: 120 }
        },
        create_datetime: {
          title: t('message.pages.miscprocurement.stationInfo.createTime'),
          type: 'datetime',
          form: { show: false },
          column: { width: 180 }
        },
        update_datetime: {
          title: t('message.pages.miscprocurement.stationInfo.updateTime'),
          type: 'datetime',
          form: { show: false },
          column: { width: 180 }
        }
      }
    }
  }
}
