import { dict, CreateCrudOptionsProps, CreateCrudOptionsRet } from '@fast-crud/fast-crud'
import * as api from './api'
import { GetCompanies } from '../currency/api'
import { useUserInfo } from '/@/stores/userInfo'
import { ElMessage } from 'element-plus'

const resetCycleDict = [
  { value: 'yy', label: '按年2（YY）' },
  { value: 'yyyy', label: '按年4（YYYY）' },
  { value: 'yymm', label: '按月4（YYMM）' },
  { value: 'yyyymm', label: '按月6（YYYYMM）' },
  { value: 'yymmdd', label: '按日6（YYMMDD）' },
  { value: 'yyyymmdd', label: '按日8（YYYYMMDD）' }
]

/** 与 `SystemNoRule.RULE_CODE_CHOICES` 一致；表单/搜索下拉展示「代码 - 名称」，列表列仅显示代码（见 column.formatter） */
const ruleCodeDict = [
  { value: 'miscQTS', label: 'miscQTS （杂采报价单）' },
  { value: 'miscRFS', label: 'miscRFS （杂采询价单）' }
]

/**
 * 交易厂区「通用」：非公司主数据，仅存于编号规则下拉；与 unique(company_code, rule_code) 兼容。
 * 取值须与后端 `SystemNoRule.DEFAULT_SYSTEM_NO_COMPANY_CODE`（`apps.pisadmin.basicinfo.models`）一致。
 */
export const SYSTEMNO_GENERAL_COMPANY_CODE = 'GENERAL'

const generalCompanyOption = () => ({
  company_code: SYSTEMNO_GENERAL_COMPANY_CODE,
  company_short_name: '通用'
})

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
    const fromApi = (Array.isArray(list) ? list : [])
      .map((c: any) => ({
        company_code: c.company_code,
        company_short_name: c.company_short_name || c.company_code || c.company_name
      }))
      .filter((c: { company_code: string }) => c.company_code !== SYSTEMNO_GENERAL_COMPANY_CODE)
    return [generalCompanyOption(), ...fromApi]
  } catch (e) {
    console.warn('加载公司列表失败', e)
    return [generalCompanyOption()]
  }
}

export const createCrudOptions = function ({ crudExpose }: Partial<CreateCrudOptionsProps>): CreateCrudOptionsRet {
  void crudExpose
  const userStore = useUserInfo()
  const currentUser =
    userStore.userInfos?.name ||
    userStore.userInfos?.username ||
    userStore.userInfos?.email ||
    ''

  const ensureRuleUnique = async (companyCode: string, ruleCode: string, currentId?: number) => {
    if (!companyCode || !ruleCode) return
    const res = await api.GetList({ company_code: companyCode, rule_code: ruleCode, page: 1, page_size: 1, pageSize: 1 })
    const list =
      res?.data?.data?.results ||
      res?.data?.results ||
      res?.data?.list ||
      res?.data ||
      res?.results ||
      res?.list ||
      []
    const exists = Array.isArray(list)
      ? list.find((item: any) => item.company_code === companyCode && item.rule_code === ruleCode)
      : null
    if (exists && (!currentId || exists.id !== currentId)) {
      throw new Error('同一交易厂区下的生成单据标识号不可重复')
    }
  }

  return {
    crudOptions: {
      form: {
        labelWidth: '120px'
      },
      request: {
        pageRequest: async (query) => api.GetList(query),
        addRequest: async ({ form }) => {
          try {
            await ensureRuleUnique(form.company_code, form.rule_code)
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
        editRequest: async ({ form, row }) => {
          try {
            await ensureRuleUnique(form.company_code, form.rule_code, row.id)
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
          title: '交易厂区',
          type: 'dict-select',
          dict: dict({
            cache: false,
            value: 'company_code',
            label: 'company_short_name',
            getData: async () => loadCompanyOptions()
          }),
          search: { show: true },
          form: {
            value: SYSTEMNO_GENERAL_COMPANY_CODE,
            rules: [{ required: true, message: '请选择交易厂区' }]
          },
          column: { minWidth: 160, showOverflowTooltip: true }
        },
        rule_code: {
          title: '生成单据标识号',
          type: 'dict-select',
          dict: dict({ data: ruleCodeDict }),
          search: {
            show: true,
            component: { props: { placeholder: '请选择', clearable: true } }
          },
          form: {
            rules: [{ required: true, message: '请选择生成单据标识号' }],
            component: { props: { placeholder: '请选择', filterable: true } }
          },
          column: {
            minWidth: 140,
            showOverflowTooltip: true,
            formatter: (ctx: { value?: unknown; row?: { rule_code?: string } }) => {
              const v = ctx.value ?? ctx.row?.rule_code
              return v === undefined || v === null || v === '' ? '' : String(v)
            }
          }
        },
        reset_cycle: {
          title: '流水码重置类别',
          type: 'dict-select',
          dict: dict({ data: resetCycleDict }),
          form: { rules: [{ required: true, message: '请选择流水码重置类别' }] },
          column: { minWidth: 180, showOverflowTooltip: true }
        },
        prefix: {
          title: '单据头',
          type: 'input',
          column: { minWidth: 140, showOverflowTooltip: true }
        },
        factory_code: {
          title: '厂区区分码',
          type: 'input',
          column: { minWidth: 140, showOverflowTooltip: true }
        },
        seq_length: {
          title: '流水码长度',
          type: 'input-number',
          form: { value: 4, component: { props: { min: 1, max: 20 } } },
          column: { width: 120 }
        },
        createuser: {
          title: '单据创建人',
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
        updateuser: {
          title: '单据修改人',
          type: 'input',
          form: { show: false },
          column: { width: 140, showOverflowTooltip: true }
        },
        update_datetime: {
          title: '修改时间',
          type: 'datetime',
          form: { show: false },
          column: { width: 180 }
        },
        sequence_date: {
          title: '流水日期',
          type: 'input',
          form: { show: false },
          column: { minWidth: 140, showOverflowTooltip: true }
        },
        prev_sequence: {
          title: '上一流水码',
          type: 'number',
          form: { show: false },
          column: { width: 120 }
        },
        current_sequence: {
          title: '下一流水码',
          type: 'number',
          form: { show: false },
          column: { width: 140 }
        },
        last_generate_user: {
          title: '单据最后产生人',
          type: 'input',
          form: { show: false },
          column: { minWidth: 150, showOverflowTooltip: true }
        },
        last_generate_time: {
          title: '单据最后产生时间',
          type: 'datetime',
          form: { show: false },
          column: { width: 190 }
        }
      }
    }
  }
}
