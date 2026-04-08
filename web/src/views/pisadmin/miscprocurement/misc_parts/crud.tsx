import { dict, CreateCrudOptionsProps, CreateCrudOptionsRet } from '@fast-crud/fast-crud'
import { useI18n } from 'vue-i18n'
import * as api from './api'
import { GetCompanies } from '../../basicinfo/currency/api'
import { GetList as GetUnits } from '../../basicinfo/unit/api'
import { ElMessage } from 'element-plus'

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

const loadUnitOptions = async (companyCode?: string) => {
  try {
    const params: any = { page: 1, page_size: 500, pageSize: 500 }
    if (companyCode) params.factory = companyCode
    const res = await GetUnits(params)
    const list =
      res?.data?.data?.results ||
      res?.data?.results ||
      res?.data?.list ||
      res?.data ||
      res?.results ||
      res?.list ||
      []
    return (Array.isArray(list) ? list : []).map((u: any) => ({
      value: u.unitcode || u.unit_code,
      label: u.unitname || u.unit_name || u.unitcode
    }))
  } catch (e) {
    console.warn('加载单位列表失败', e)
    return []
  }
}

void loadCompanyOptions()

export const createCrudOptions = function ({ crudExpose }: CreateCrudOptionsProps): CreateCrudOptionsRet {
  const { t } = useI18n()
  void crudExpose

  const statusDict = () => [
    { value: 1, label: t('message.pages.miscprocurement.misc_parts.statusEnabled') },
    { value: 0, label: t('message.pages.miscprocurement.misc_parts.statusDisabled') }
  ]

  const categoryDict = () => [
    { value: 1, label: t('message.pages.miscprocurement.misc_parts.categoryTooling') },
    { value: 2, label: t('message.pages.miscprocurement.misc_parts.categoryGraphite') },
    { value: 3, label: t('message.pages.miscprocurement.misc_parts.categoryOther') }
  ]

  const ensurePartUnique = async (companyCode: string, partId: string, currentId?: number) => {
    if (!companyCode || !partId) return
    const res = await api.GetList({ company_code: companyCode, partid: partId, page: 1, page_size: 1, pageSize: 1 })
    const list =
      res?.data?.data?.results ||
      res?.data?.results ||
      res?.data?.list ||
      res?.data ||
      res?.results ||
      res?.list ||
      []
    const exists = Array.isArray(list)
      ? list.find((item: any) => item.company_code === companyCode && item.partid === partId)
      : null
    if (exists && (!currentId || exists.id !== currentId)) {
      throw new Error(t('message.pages.miscprocurement.misc_parts.companyCode') + t('message.pages.miscprocurement.misc_parts.partid') + t('message.pages.miscprocurement.misc_parts.validation.alreadyExists'))
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
            await ensurePartUnique(form.company_code, form.partid)
            return await api.AddObj(form)
          } catch (err: any) {
            ElMessage.error(err?.message || '保存失败')
            throw err
          }
        },
        editRequest: async ({ form, row }) => {
          try {
            await ensurePartUnique(form.company_code, form.partid, row.id)
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
          title: t('message.pages.miscprocurement.misc_parts.companyCode'),
          type: 'dict-select',
          dict: dict({
            cache: false,
            value: 'company_code',
            label: 'company_short_name',
            getData: async () => loadCompanyOptions()
          }),
          search: { show: true },
          form: {
            component: {
              on: {
                change({ form, value }: any) {
                  form.unit = undefined
                  form.company_code = value
                }
              }
            }
          },
          column: { minWidth: 160, showOverflowTooltip: true }
        },
        partid: {
          title: t('message.pages.miscprocurement.misc_parts.partid'),
          type: 'input',
          search: { show: true, component: { props: { placeholder: t('message.pages.miscprocurement.misc_parts.partid'), clearable: true } } },
          form: { rules: [{ required: true, message: t('message.pages.miscprocurement.misc_parts.partid') + ' ' + t('message.pages.menu.validation.fieldNameRequired') }] },
          column: { minWidth: 160, showOverflowTooltip: true }
        },
        partid_name: {
          title: t('message.pages.miscprocurement.misc_parts.partidName'),
          type: 'input',
          form: { rules: [{ required: true, message: t('message.pages.miscprocurement.misc_parts.partidName') + ' ' + t('message.pages.menu.validation.fieldNameRequired') }] },
          column: { minWidth: 160, showOverflowTooltip: true }
        },
        specification: {
          title: t('message.pages.miscprocurement.misc_parts.specification'),
          type: 'input',
          form: { rules: [{ required: true, message: t('message.pages.miscprocurement.misc_parts.specification') + ' ' + t('message.pages.menu.validation.fieldNameRequired') }] },
          column: { minWidth: 160, showOverflowTooltip: true }
        },
        unit: {
          title: t('message.pages.miscprocurement.misc_parts.unit'),
          type: 'dict-select',
          dict: dict({
            cache: false,
            getData: async ({ form }: any = {}) => loadUnitOptions(form?.company_code)
          }),
          form: { rules: [{ required: true, message: t('message.pages.miscprocurement.misc_parts.unit') + ' ' + t('message.pages.menu.validation.fieldNameRequired') }], component: { props: { placeholder: t('message.pages.miscprocurement.misc_parts.companyCode') } } },
          column: { width: 140, showOverflowTooltip: true }
        },
        partid_category_id: {
          title: t('message.pages.miscprocurement.misc_parts.partidCategory'),
          type: 'dict-select',
          dict: dict({ data: categoryDict() }),
          column: { width: 140, showOverflowTooltip: true }
        },
        status: {
          title: t('message.pages.miscprocurement.misc_parts.status'),
          type: 'dict-switch',
          dict: dict({ data: statusDict() }),
          form: { value: 1 },
          column: { width: 120 }
        },
        create_datetime: {
          title: t('message.pages.miscprocurement.misc_parts.createTime'),
          type: 'datetime',
          form: { show: false },
          column: { width: 180 }
        },
        update_datetime: {
          title: t('message.pages.miscprocurement.misc_parts.updateTime'),
          type: 'datetime',
          form: { show: false },
          column: { width: 180 }
        }
      }
    }
  }
}
