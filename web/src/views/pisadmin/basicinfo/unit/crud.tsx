import { dict, CreateCrudOptionsProps, CreateCrudOptionsRet } from '@fast-crud/fast-crud'
import * as api from './api'
import { ElMessage } from 'element-plus'

const statusDict = [
  { value: 1, label: '可用' },
  { value: 0, label: '不可用' }
]

export const createCrudOptions = function ({ crudExpose }: CreateCrudOptionsProps): CreateCrudOptionsRet {
  void crudExpose

  const ensureUnitCodeUnique = async (code: string, currentId?: number) => {
    if (!code) return
    const res = await api.GetList({ unitcode: code, page: 1, page_size: 1, pageSize: 1 })
    const list =
      res?.data?.data?.results ||
      res?.data?.results ||
      res?.data?.list ||
      res?.data ||
      res?.results ||
      res?.list ||
      []
    const exists = Array.isArray(list) ? list.find((item: any) => item.unitcode === code) : null
    if (exists && (!currentId || exists.id !== currentId)) {
      throw new Error('计量单位代码已存在，不可重复')
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
            await ensureUnitCodeUnique(form.unitcode)
            return await api.AddObj(form)
          } catch (err: any) {
            ElMessage.error(err?.message || '保存失败')
            throw err
          }
        },
        editRequest: async ({ form, row }) => {
          try {
            await ensureUnitCodeUnique(form.unitcode, row.id)
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
        unitcode: {
          title: '计量单位代码',
          type: 'input',
          search: { show: true, component: { props: { placeholder: '请输入计量单位代码', clearable: true } } },
          form: { rules: [{ required: true, message: '请输入计量单位代码' }] },
          column: { minWidth: 140, showOverflowTooltip: true }
        },
        unitname: {
          title: '计量单位名称',
          type: 'input',
          search: { show: true, component: { props: { placeholder: '请输入计量单位名称', clearable: true } } },
          form: { rules: [{ required: true, message: '请输入计量单位名称' }] },
          column: { minWidth: 160, showOverflowTooltip: true }
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
