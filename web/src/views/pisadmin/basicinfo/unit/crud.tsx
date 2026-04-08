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
        unitcode: {
          title: t('message.pages.basicinfo.unit.unitcode'),
          type: 'input',
          search: { show: true, component: { props: { placeholder: t('message.pages.basicinfo.unit.unitcode'), clearable: true } } },
          form: { rules: [{ required: true, message: t('message.pages.basicinfo.unit.unitcode') + ' ' + t('message.pages.menu.validation.fieldNameRequired') }] },
          column: { minWidth: 140, showOverflowTooltip: true }
        },
        unitname: {
          title: t('message.pages.basicinfo.unit.unitname'),
          type: 'input',
          search: { show: true, component: { props: { placeholder: t('message.pages.basicinfo.unit.unitname'), clearable: true } } },
          form: { rules: [{ required: true, message: t('message.pages.basicinfo.unit.unitname') + ' ' + t('message.pages.menu.validation.fieldNameRequired') }] },
          column: { minWidth: 160, showOverflowTooltip: true }
        },
        status: {
          title: t('message.pages.basicinfo.unit.status'),
          type: 'dict-switch',
          dict: dict({ data: [{ value: 1, label: t('message.pages.basicinfo.unit.enabled') }, { value: 0, label: t('message.pages.basicinfo.unit.disabled') }] }),
          form: { value: 1 },
          column: { width: 120 }
        },
        create_datetime: {
          title: t('message.pages.basicinfo.unit.createTime'),
          type: 'datetime',
          form: { show: false },
          column: { width: 180 }
        },
        update_datetime: {
          title: t('message.pages.basicinfo.unit.updateTime'),
          type: 'datetime',
          form: { show: false },
          column: { width: 180 }
        }
      }
    }
  }
}
