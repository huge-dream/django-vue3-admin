import { dict, CreateCrudOptionsProps, CreateCrudOptionsRet } from '@fast-crud/fast-crud'
import * as api from './api'
import { useUserInfo } from '/@/stores/userInfo'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'

export const createCrudOptions = function ({ crudExpose }: Partial<CreateCrudOptionsProps>): CreateCrudOptionsRet {
  void crudExpose
  const { t } = useI18n()
  const userStore = useUserInfo()
  const currentUser =
    userStore.userInfos?.name ||
    userStore.userInfos?.username ||
    userStore.userInfos?.email ||
    ''

  const ensureCompanyCodeUnique = async (code: string, currentId?: number) => {
    if (!code) return
    const res = await api.GetList({ company_code: code, page: 1, page_size: 1, pageSize: 1 })
    const list =
      res?.data?.data?.results ||
      res?.data?.results ||
      res?.data?.list ||
      res?.data ||
      res?.results ||
      res?.list ||
      []
    const exists = Array.isArray(list) ? list.find((item: any) => item.company_code === code) : null
    if (exists && (!currentId || exists.id !== currentId)) {
      throw new Error(t('message.pages.basicinfo.company.companyCode') + t('message.pages.menu.validation.alreadyExists'))
    }
  }
  return {
    crudOptions: {
      form: {
        labelWidth: '110px',
        display: 'flex'
      },
      request: {
        pageRequest: async (query) => api.GetList(query),
        addRequest: async ({ form }) =>
          {
            try {
              await ensureCompanyCodeUnique(form.company_code)
              return await api.AddObj({
                ...form,
                createuser: currentUser,
                updateuser: currentUser
              })
            } catch (err: any) {
              ElMessage.error(err?.message || '保存失败')
              throw err
            }
          },
        editRequest: async ({ form, row }) =>
          {
            try {
              await ensureCompanyCodeUnique(form.company_code, row.id)
              return await api.UpdateObj({
                ...form,
                id: row.id,
                updateuser: currentUser
              })
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
          title: t('message.pages.basicinfo.company.companyCode'),
          type: 'input',
          search: { show: true, component: { props: { placeholder: t('message.pages.basicinfo.company.companyCode'), clearable: true } } },
          form: { rules: [{ required: true, message: t('message.pages.basicinfo.company.companyCode') + ' ' + t('message.pages.menu.validation.fieldNameRequired') }] },
          editForm: {
            component: { props: { disabled: true } }
          },
          column: { minWidth: 140, showOverflowTooltip: true }
        },
        company_name: {
          title: t('message.pages.basicinfo.company.companyName'),
          type: 'input',
          search: { show: true, component: { props: { placeholder: t('message.pages.basicinfo.company.companyName'), clearable: true } } },
          column: { minWidth: 180, showOverflowTooltip: true }
        },
        company_short_name: {
          title: t('message.pages.basicinfo.company.companyShortName'),
          type: 'input',
          column: { minWidth: 150, showOverflowTooltip: true }
        },
        company_address: {
          title: t('message.pages.basicinfo.company.companyAddress'),
          type: 'input',
          column: { minWidth: 220, showOverflowTooltip: true }
        },
        status: {
          title: t('message.pages.basicinfo.company.status'),
          type: 'dict-switch',
          dict: dict({ data: [{ value: 1, label: t('message.pages.basicinfo.company.enabled') }, { value: 0, label: t('message.pages.basicinfo.company.disabled') }] }),
          form: { value: 1 },
          column: { width: 120 }
        },
        createuser: {
          title: t('message.pages.basicinfo.company.createTime'),
          type: 'input',
          form: { show: false },
          column: { width: 140, showOverflowTooltip: true }
        },
        updateuser: {
          title: t('message.pages.basicinfo.company.updateTime'),
          type: 'input',
          form: { show: false },
          column: { width: 140, showOverflowTooltip: true }
        },
        create_datetime: {
          title: t('message.pages.basicinfo.company.createTime'),
          type: 'datetime',
          form: { show: false },
          column: { width: 180 }
        },
        update_datetime: {
          title: t('message.pages.basicinfo.company.updateTime'),
          type: 'datetime',
          form: { show: false },
          column: { width: 180 }
        }
      }
    }
  }
}
