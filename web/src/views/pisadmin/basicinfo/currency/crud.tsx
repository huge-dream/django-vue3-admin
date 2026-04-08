import { dict, CreateCrudOptionsProps, CreateCrudOptionsRet } from '@fast-crud/fast-crud'
import * as api from './api'
import { useI18n } from 'vue-i18n'

export const createCrudOptions = function ({ crudExpose }: Partial<CreateCrudOptionsProps>): CreateCrudOptionsRet {
  void crudExpose
  const { t } = useI18n()

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
          title: t('message.pages.basicinfo.currency.currencyname'),
          type: 'input',
          search: { show: true, component: { props: { placeholder: t('message.pages.basicinfo.currency.currencyname'), clearable: true } } },
          form: { rules: [{ required: true, message: t('message.pages.basicinfo.currency.currencyname') + ' ' + t('message.pages.menu.validation.fieldNameRequired') }] },
          column: { minWidth: 160, showOverflowTooltip: true }
        },
        currencycode: {
          title: t('message.pages.basicinfo.currency.currencycode'),
          type: 'input',
          search: { show: true, component: { props: { placeholder: t('message.pages.basicinfo.currency.currencycode'), clearable: true } } },
          form: { rules: [{ required: true, message: t('message.pages.basicinfo.currency.currencycode') + ' ' + t('message.pages.menu.validation.fieldNameRequired') }] },
          editForm: {
            component: { props: { disabled: true } }
          },
          column: { minWidth: 140, showOverflowTooltip: true }
        },
        currencysymbol: {
          title: t('message.pages.basicinfo.currency.currencysymbol'),
          type: 'input',
          form: { rules: [{ required: true, message: t('message.pages.basicinfo.currency.currencysymbol') + ' ' + t('message.pages.menu.validation.fieldNameRequired') }] },
          column: { width: 120, showOverflowTooltip: true }
        },
        factory: {
          title: t('message.pages.basicinfo.currency.factory'),
          type: 'dict-select',
          dict: dict({
            cache: false,
            value: 'company_code',
            label: 'company_short_name',
            getData: async () => {
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
                return []
              }
            }
          }),
          search: { show: true },
          form: { rules: [{ required: true, message: t('message.pages.basicinfo.currency.factory') + ' ' + t('message.pages.menu.validation.fieldNameRequired') }] },
          column: { width: 160, showOverflowTooltip: true }
        },
        tax: {
          title: t('message.pages.basicinfo.currency.tax') + '(%)',
          type: 'number',
          form: { rules: [{ required: true, message: t('message.pages.basicinfo.currency.tax') + ' ' + t('message.pages.menu.validation.fieldNameRequired') }], component: { props: { precision: 2 } } },
          column: { width: 120 }
        },
        status: {
          title: t('message.pages.basicinfo.currency.status'),
          type: 'dict-switch',
          dict: dict({ data: [{ value: 1, label: t('message.pages.basicinfo.currency.enabled') }, { value: 0, label: t('message.pages.basicinfo.currency.disabled') }] }),
          form: { value: 1 },
          column: { width: 120 }
        },
        create_datetime: {
          title: t('message.pages.basicinfo.currency.createTime'),
          type: 'datetime',
          form: { show: false },
          column: { width: 180 }
        },
        update_datetime: {
          title: t('message.pages.basicinfo.currency.updateTime'),
          type: 'datetime',
          form: { show: false },
          column: { width: 180 }
        }
      }
    }
  }
}
