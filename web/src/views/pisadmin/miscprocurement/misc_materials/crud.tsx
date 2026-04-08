import { dict, CreateCrudOptionsProps, CreateCrudOptionsRet } from '@fast-crud/fast-crud'
import { useI18n } from 'vue-i18n'
import * as api from './api'
import { GetCompanies } from '../../basicinfo/currency/api'

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

void loadCompanyOptions()

export const createCrudOptions = function ({ crudExpose }: CreateCrudOptionsProps): CreateCrudOptionsRet {
  void crudExpose
  const { t } = useI18n()

  const statusDict = [
    { value: 1, label: t('message.pages.miscprocurement.misc_materials.statusEnabled') },
    { value: 0, label: t('message.pages.miscprocurement.misc_materials.statusDisabled') }
  ]

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
        factory: {
          title: t('message.pages.miscprocurement.misc_materials.companyCode'),
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
          column: { minWidth: 160, showOverflowTooltip: true }
        },
        materialtype: {
          title: t('message.pages.miscprocurement.misc_materials.materialtype'),
          type: 'input',
          search: {
            show: true,
            component: { props: { placeholder: t('message.pages.miscprocurement.misc_materials.materialtype'), clearable: true } }
          },
          column: { minWidth: 160, showOverflowTooltip: true }
        },
        density: {
          title: t('message.pages.miscprocurement.misc_materials.density'),
          type: 'input',
          form: { rules: [{ required: true, message: t('message.pages.miscprocurement.misc_materials.density') + ' ' + t('message.pages.menu.validation.fieldNameRequired') }] },
          column: { width: 120, showOverflowTooltip: true }
        },
        price: {
          title: t('message.pages.miscprocurement.misc_materials.price'),
          type: 'number',
          form: { rules: [{ required: true, message: t('message.pages.miscprocurement.misc_materials.price') + ' ' + t('message.pages.menu.validation.fieldNameRequired') }], component: { props: { precision: 2 } } },
          column: { width: 120 }
        },
        status: {
          title: t('message.pages.miscprocurement.misc_materials.status'),
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
