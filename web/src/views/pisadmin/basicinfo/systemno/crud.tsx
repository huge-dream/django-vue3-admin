import { dict, CreateCrudOptionsProps, CreateCrudOptionsRet } from '@fast-crud/fast-crud'
import * as api from './api'
import { GetCompanies } from '../currency/api'
import { useUserInfo } from '/@/stores/userInfo'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'

/**
 * 交易厂区「通用」：非公司主数据，仅存于编号规则下拉；与 unique(company_code, rule_code) 兼容。
 * 取值须与后端 `SystemNoRule.DEFAULT_SYSTEM_NO_COMPANY_CODE`（`apps.pisadmin.basicinfo.models`）一致。
 */
export const SYSTEMNO_GENERAL_COMPANY_CODE = 'GENERAL'

const loadCompanyOptions = async (generalLabel: string) => {
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
    return [{ company_code: SYSTEMNO_GENERAL_COMPANY_CODE, company_short_name: generalLabel }, ...fromApi]
  } catch (e) {
    console.warn('加载公司列表失败', e)
    return [{ company_code: SYSTEMNO_GENERAL_COMPANY_CODE, company_short_name: generalLabel }]
  }
}

export const createCrudOptions = function ({ crudExpose }: Partial<CreateCrudOptionsProps>): CreateCrudOptionsRet {
  const { t } = useI18n()
  void crudExpose
  const userStore = useUserInfo()
  const currentUser =
    userStore.userInfos?.name ||
    userStore.userInfos?.username ||
    userStore.userInfos?.email ||
    ''

  const resetCycleDict = [
    { value: 'yy', label: t('message.pages.basicinfo.systemNo.resetCycleYy2') },
    { value: 'yyyy', label: t('message.pages.basicinfo.systemNo.resetCycleYyyy4') },
    { value: 'yymm', label: t('message.pages.basicinfo.systemNo.resetCycleYymm4') },
    { value: 'yyyymm', label: t('message.pages.basicinfo.systemNo.resetCycleYyyymm6') },
    { value: 'yymmdd', label: t('message.pages.basicinfo.systemNo.resetCycleYymmdd6') },
    { value: 'yyyymmdd', label: t('message.pages.basicinfo.systemNo.resetCycleYyyymmdd8') }
  ]

  /** 与 `SystemNoRule.RULE_CODE_CHOICES` 一致；表单/搜索下拉展示「代码 - 名称」，列表列仅显示代码（见 column.formatter） */
  const ruleCodeDict = [
    { value: 'miscQTS', label: t('message.pages.basicinfo.systemNo.ruleCodeMiscQts') },
    { value: 'miscRFS', label: t('message.pages.basicinfo.systemNo.ruleCodeMiscRfs') }
  ]

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
      throw new Error(t('message.pages.basicinfo.systemNo.companyCode') + t('message.pages.basicinfo.systemNo.ruleCode') + t('message.pages.menu.validation.alreadyExists'))
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
          title: t('message.pages.basicinfo.systemNo.companyCode'),
          type: 'dict-select',
          dict: dict({
            cache: false,
            value: 'company_code',
            label: 'company_short_name',
            getData: async () => loadCompanyOptions(t('message.pages.basicinfo.systemNo.general'))
          }),
          search: { show: true },
          form: {
            value: SYSTEMNO_GENERAL_COMPANY_CODE,
            rules: [{ required: true, message: t('message.pages.basicinfo.systemNo.companyCode') + ' ' + t('message.pages.menu.validation.fieldNameRequired') }]
          },
          column: { minWidth: 160, showOverflowTooltip: true }
        },
        rule_code: {
          title: t('message.pages.basicinfo.systemNo.ruleCode'),
          type: 'dict-select',
          dict: dict({ data: ruleCodeDict }),
          search: {
            show: true,
            component: { props: { placeholder: t('message.pages.menu.buttons.select'), clearable: true } }
          },
          form: {
            rules: [{ required: true, message: t('message.pages.basicinfo.systemNo.ruleCode') + ' ' + t('message.pages.menu.validation.fieldNameRequired') }],
            component: { props: { placeholder: t('message.pages.menu.buttons.select'), filterable: true } }
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
          title: t('message.pages.basicinfo.systemNo.resetCycle'),
          type: 'dict-select',
          dict: dict({ data: resetCycleDict }),
          form: { rules: [{ required: true, message: t('message.pages.basicinfo.systemNo.resetCycle') + ' ' + t('message.pages.menu.validation.fieldNameRequired') }] },
          column: { minWidth: 180, showOverflowTooltip: true }
        },
        prefix: {
          title: t('message.pages.basicinfo.systemNo.prefix'),
          type: 'input',
          column: { minWidth: 140, showOverflowTooltip: true }
        },
        factory_code: {
          title: t('message.pages.basicinfo.systemNo.factoryCode'),
          type: 'input',
          column: { minWidth: 140, showOverflowTooltip: true }
        },
        seq_length: {
          title: t('message.pages.basicinfo.systemNo.seqLength'),
          type: 'input-number',
          form: { value: 4, component: { props: { min: 1, max: 20 } } },
          column: { width: 120 }
        },
        createuser: {
          title: t('message.pages.basicinfo.systemNo.createUser'),
          type: 'input',
          form: { show: false },
          column: { width: 140, showOverflowTooltip: true }
        },
        create_datetime: {
          title: t('message.pages.basicinfo.systemNo.createTime'),
          type: 'datetime',
          form: { show: false },
          column: { width: 180 }
        },
        updateuser: {
          title: t('message.pages.basicinfo.systemNo.updateUser'),
          type: 'input',
          form: { show: false },
          column: { width: 140, showOverflowTooltip: true }
        },
        update_datetime: {
          title: t('message.pages.basicinfo.systemNo.updateTime'),
          type: 'datetime',
          form: { show: false },
          column: { width: 180 }
        },
        sequence_date: {
          title: t('message.pages.basicinfo.systemNo.sequenceDate'),
          type: 'input',
          form: { show: false },
          column: { minWidth: 140, showOverflowTooltip: true }
        },
        prev_sequence: {
          title: t('message.pages.basicinfo.systemNo.prevSequence'),
          type: 'number',
          form: { show: false },
          column: { width: 120 }
        },
        current_sequence: {
          title: t('message.pages.basicinfo.systemNo.currentSequence'),
          type: 'number',
          form: { show: false },
          column: { width: 140 }
        },
        last_generate_user: {
          title: t('message.pages.basicinfo.systemNo.lastGenerateUser'),
          type: 'input',
          form: { show: false },
          column: { minWidth: 150, showOverflowTooltip: true }
        },
        last_generate_time: {
          title: t('message.pages.basicinfo.systemNo.lastGenerateTime'),
          type: 'datetime',
          form: { show: false },
          column: { width: 190 }
        }
      }
    }
  }
}
