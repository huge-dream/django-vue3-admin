import { dict, CreateCrudOptionsProps, CreateCrudOptionsRet } from '@fast-crud/fast-crud'
import * as api from './api'
import { useUserInfo } from '/@/stores/userInfo'
import { ElMessage } from 'element-plus'

const statusDict = [
  { value: 1, label: '可用' },
  { value: 0, label: '不可用' }
]

export const createCrudOptions = function ({ crudExpose }: Partial<CreateCrudOptionsProps>): CreateCrudOptionsRet {
  void crudExpose
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
      throw new Error('公司代码已存在，不可重复')
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
          title: '公司代码',
          type: 'input',
          search: { show: true, component: { props: { placeholder: '请输入公司代码', clearable: true } } },
          form: { rules: [{ required: true, message: '请输入公司代码' }] },
          column: { minWidth: 140, showOverflowTooltip: true }
        },
        company_name: {
          title: '公司全称',
          type: 'input',
          search: { show: true, component: { props: { placeholder: '请输入公司全称', clearable: true } } },
          column: { minWidth: 180, showOverflowTooltip: true }
        },
        company_short_name: {
          title: '公司简称',
          type: 'input',
          column: { minWidth: 150, showOverflowTooltip: true }
        },
        company_address: {
          title: '公司地址',
          type: 'input',
          column: { minWidth: 220, showOverflowTooltip: true }
        },
        status: {
          title: '可用状态',
          type: 'dict-switch',
          dict: dict({ data: statusDict }),
          form: { value: 1 },
          column: { width: 120 }
        },
        createuser: {
          title: '创建人员',
          type: 'input',
          form: { show: false },
          column: { width: 140, showOverflowTooltip: true }
        },
        updateuser: {
          title: '更新人员',
          type: 'input',
          form: { show: false },
          column: { width: 140, showOverflowTooltip: true }
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
