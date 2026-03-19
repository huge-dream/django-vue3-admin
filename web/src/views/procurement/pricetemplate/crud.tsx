import { dict, CreateCrudOptionsProps, CreateCrudOptionsRet } from '@fast-crud/fast-crud'
import * as api from './api'
import SectionBuilder from './SectionBuilder.vue'

// 后端 cost_template.procurement_category：1=策采；2=杂采
const procurementDict = [
  { value: '1', label: '策采' },
  { value: '2', label: '杂采' }
]

const logPT = (...args: any[]) => console.log('[CostTemplate]', ...args)

type SupplierBehavior =
  | 'prefill_locked'
  | 'prefill_editable'
  | 'hidden_required'
  | 'hidden_optional'
  | 'required'
  | 'optional'

type FieldOpts = { supplierEditable?: boolean; supplierRequired?: boolean; supplierBehavior?: SupplierBehavior }

const supplierBehaviorCodeMap: Record<SupplierBehavior, number> = {
  prefill_locked: 1,
  prefill_editable: 2,
  hidden_required: 3,
  hidden_optional: 4,
  required: 5,
  optional: 6
}

const legacySupplierBehavior = (purchaserRequired: boolean, supplierRequired: boolean, supplierEditable: boolean): SupplierBehavior => {
  if (purchaserRequired) {
    if (supplierRequired && !supplierEditable) return 'prefill_locked'
    if (supplierRequired && supplierEditable) return 'prefill_editable'
    if (!supplierRequired && !supplierEditable) return 'hidden_required'
    return 'hidden_optional'
  }
  return supplierRequired ? 'required' : 'optional'
}

const normalizeSupplierBehavior = (
  raw: unknown,
  purchaserRequired = false,
  supplierRequired = false,
  supplierEditable = true
): SupplierBehavior => {
  if (typeof raw === 'string' && raw in supplierBehaviorCodeMap) {
    return raw as SupplierBehavior
  }
  const code = Number(raw)
  if (Number.isInteger(code) && code >= 1 && code <= 6) {
    return (Object.keys(supplierBehaviorCodeMap) as SupplierBehavior[]).find((key) => supplierBehaviorCodeMap[key] === code) || 'optional'
  }
  return legacySupplierBehavior(purchaserRequired, supplierRequired, supplierEditable)
}

const getSupplierRequiredCode = (field: any) =>
  field?.autoFill
    ? 0
    :
  supplierBehaviorCodeMap[
    normalizeSupplierBehavior(
      field?.supplier_required ?? field?.supplierRequiredCode ?? field?.supplierBehavior,
      !!field?.purchaserRequired,
      !!field?.supplierRequired,
      field?.supplierEditable !== false
    )
  ] || 0

const createField = (
  label: string,
  key: string,
  type: 'text' | 'select' | 'number',
  formula = '',
  opts: FieldOpts = {}
) => {
  const supplierRequired = opts.supplierRequired === true
  const supplierEditable = opts.supplierEditable !== false
  const supplierBehavior =
    opts.supplierBehavior || legacySupplierBehavior(false, supplierRequired, supplierEditable)
  return {
    label,
    key,
    type,
    formula,
    fixed: true,
    purchaserRequired: false,
    supplierBehavior,
    builtIn: true
  }
}

const materialsFieldsMisc = [
  createField('材质', 'material', 'text'),
  createField('长', 'length', 'number'),
  createField('宽', 'width', 'number'),
  createField('高', 'height', 'number'),
  createField('比重', 'specificgravity', 'number', '根据材质自动带出', { supplierEditable: false }),
  createField('数量', 'qty', 'number', '', { supplierRequired: true }),
  createField('重量', 'weight', 'number', '长*宽*高*比重*数量', { supplierEditable: false }),
  createField('单价', 'unitPrice', 'number'),
  createField('材料费用', 'material_cost', 'number', '重量*单价', { supplierEditable: false })
]

const materialsFieldsStrategic = [
  createField('材质', 'material', 'text'),
  createField('用量/重量', 'weight', 'number'),
  createField('单价', 'unitPrice', 'number'),
  createField('单位', 'unit', 'text'),
  createField('损耗率', 'loss_rate', 'number'),
  createField('材料费用', 'material_cost', 'number', '重量*单价', { supplierEditable: false }),
  createField('备注', 'remark', 'text')
]

const getMaterialsFields = (procurementCategory?: string) =>
  procurementCategory === '1' ? materialsFieldsStrategic : materialsFieldsMisc

const processFieldsMisc = [
  createField('加工工站', 'process_station', 'select'),
  createField('单位', 'unit', 'text', '', { supplierEditable: false }),
  createField('费率', 'unitrate', 'number', '根据工站自动带出', { supplierEditable: false }),
  createField('加工计量', 'processqty', 'number'),
  createField('加工费', 'processprice', 'number', '费率*加工计量', { supplierEditable: false }),
  createField('备注', 'remark', 'text', '', { supplierEditable: false })
]

const processFieldsStrategic = [
  createField('加工工站', 'process_station', 'select'),
  createField('加工时间', 'process_time', 'number'),
  createField('加工单价', 'unit_price', 'number'),
  createField('单位', 'unit', 'text', '', { supplierEditable: false }),
  createField('损耗率', 'loss_rate', 'number', '', { supplierEditable: false }),
  createField('加工费', 'process_cost', 'number', '', { supplierEditable: false }),
  createField('备注', 'remark', 'text', '', { supplierEditable: false })
]

const getProcessFields = (procurementCategory?: string) =>
  procurementCategory === '1' ? processFieldsStrategic : processFieldsMisc

const normalizeSections = (value: unknown) => {
  if (value === null || value === undefined || (typeof value === 'string' && value.trim() === '')) {
    return []
  }
  if (typeof value === 'string') {
    try {
      const parsed = JSON.parse(value)
      return Array.isArray(parsed) ? parsed : []
    } catch (e) {
      return []
    }
  }
  if (Array.isArray(value)) {
    return value
  }
  return []
}

const baseSections: Record<string, any> = {
  产品明细: {
    id: 'productDetail',
    title: '产品明细',
    enabled: true,
    supplierCanAddRow: true,
    allowAddField: true,
    fields: [
      createField('料号', 'partNo', 'text'),
      createField('规格描述', 'desc', 'text'),
      createField('数量', 'qty', 'number'),
      createField('单价', 'price', 'number'),
      createField('合计价格', 'amount', 'number', '数量*单价', { supplierEditable: false })
    ]
  },
  材料成本: {
    id: 'materials',
    title: '材料成本',
    enabled: true,
    supplierCanAddRow: true,
    allowAddField: true,
    fields: []
  },
  加工成本: {
    id: 'process',
    title: '加工成本',
    enabled: true,
    supplierCanAddRow: true,
    allowAddField: true,
    fields: []
  },
  管销研费用: {
    id: 'sgna',
    title: '管销研费用',
    enabled: true,
    supplierCanAddRow: false,
    allowAddField: false,
    fields: [createField('费用', 'fee', 'number')]
  },
  其它成本: {
    id: 'others',
    title: '其它成本',
    enabled: true,
    supplierCanAddRow: true,
    allowAddField: false,
    fields: [
      createField('包装费', 'packaging_cost', 'number'),
      createField('运输费', 'transportation_cost', 'number')
    ]
  },
  利润: {
    id: 'profit',
    title: '利润',
    enabled: true,
    supplierCanAddRow: false,
    allowAddField: false,
    fields: [
      createField('利润率', 'profitRate', 'number')
    ]
  },
  税金: {
    id: 'tax',
    title: '税金',
    enabled: true,
    supplierCanAddRow: false,
    allowAddField: false,
    fields: [
      createField('税率', 'taxRate', 'number', '根据交易厂区自动带出', { supplierEditable: false })
    ]
  }
}

const deepCopy = <T,>(obj: T): T => JSON.parse(JSON.stringify(obj))

const buildDefaultSections = (procurementCategory?: string) => {
  const sections = Object.values(baseSections).map((s) => deepCopy(s))
  const materials = sections.find((s) => s.title === '材料成本')
  if (materials) {
    materials.fields = deepCopy(getMaterialsFields(procurementCategory))
  }
  const process = sections.find((s) => s.title === '加工成本')
  if (process) {
    process.fields = deepCopy(getProcessFields(procurementCategory))
  }
  return sections
}

const titleAliases: Record<string, string> = {
  其它: '其它成本',
  其他: '其它成本',
  其他费用: '其它成本',
  税率: '税金',
  管销研: '管销研费用',
  管销研成本: '管销研费用'
}

const normalizeTitleKey = (title?: string) => {
  if (!title) return ''
  return titleAliases[title] || title
}

const applyEnabledFlags = (sections: any[], titles: string[]) => {
  const set = new Set(titles.map((t) => normalizeTitleKey(t)))
  sections.forEach((s) => {
    s.enabled = set.has(normalizeTitleKey(s?.title || s?.name))
  })
}

const visibleTitles = (procurementCategory?: string, enableCostStructure?: boolean) => {
  // 杂采(2) 不显示“管销研费用”
  if (procurementCategory === '2') {
    return enableCostStructure
      ? ['材料成本', '加工成本', '其它成本', '利润', '税金']
      : ['产品明细', '利润', '税金']
  }
  return enableCostStructure
    ? ['材料成本', '加工成本', '其它成本', '管销研费用', '利润', '税金']
    : ['产品明细', '利润', '税金']
}

const ensureAllSections = (form: any, titlesForEnabled?: string[], procurementCategory?: string) => {
  const existing = normalizeSections(form?.sections)
  const map = new Map<string, any>()
  existing.forEach((s: any) => {
    const key = normalizeTitleKey(s?.title || s?.name)
    if (key) map.set(key, s)
  })
  const defaults = buildDefaultSections(procurementCategory || form?.procurement_category)
  defaults.forEach((base) => {
    if (!map.has(base.title)) {
      map.set(base.title, deepCopy(base))
    }
  })
  const arr = Array.from(map.values())
  // Always replace材料成本字段按采购类别
  const materials = arr.find((s: any) => s?.title === '材料成本')
  if (materials) {
    if (!Array.isArray(materials.fields) || !materials.fields.length) {
      materials.fields = deepCopy(getMaterialsFields(procurementCategory || form?.procurement_category))
    }
  }
  // Only backfill加工成本字段，若已有自定义行不覆盖
  const process = arr.find((s: any) => s?.title === '加工成本')
  if (process) {
    if (!Array.isArray(process.fields) || !process.fields.length) {
      process.fields = deepCopy(getProcessFields(procurementCategory || form?.procurement_category))
    }
  }
  if (titlesForEnabled && titlesForEnabled.length) {
    applyEnabledFlags(arr, titlesForEnabled)
  }
  return arr
}

const refreshSectionsIfNeeded = (form: any, overrides: any = {}) => {
  const titles = visibleTitles(
    overrides.procurement_category ?? form?.procurement_category,
    overrides.enable_cost_structure ?? (form?.is_bom || 'Y') === 'Y'
  )
  const procurementCategory = overrides.procurement_category ?? form?.procurement_category
  form.sections = ensureAllSections({ ...form, ...overrides }, titles, procurementCategory)
  form.__visibleTitles = titles
  if (Array.isArray(form.sections)) {
    ;(form.sections as any).__visibleTitles = titles
  }
  latestSectionDraft = normalizeSections(form.sections)
  logPT('refreshSections', {
    procurement_category: overrides.procurement_category ?? form?.procurement_category,
    enable_cost_structure: overrides.enable_cost_structure ?? (form?.is_bom || 'Y') === 'Y',
    titles,
    sectionsCount: Array.isArray(form.sections) ? form.sections.length : 0,
    draftSectionsCount: latestSectionDraft.length
  })
}

const titleToCostCategory: Record<string, string> = {
  材料成本: '1',
  加工成本: '2',
  其它成本: '3',
  其他成本: '3',
  管销研费用: '4',
  利润: '5',
  税金: '6',
  产品明细: '7'
}

const costCategoryToTitle: Record<string, string> = {
  '1': '材料成本',
  '2': '加工成本',
  '3': '其它成本',
  '4': '管销研费用',
  '5': '利润',
  '6': '税金',
  '7': '产品明细'
}

// 绕过 fast-crud 对自定义组件深层回写偶发失效的问题：
// SectionBuilder 会把当前界面的最新分段草稿主动回传到这里，保存时优先使用这份草稿。
let latestSectionDraft: any[] = []

const countSectionFields = (sections: any[]) =>
  normalizeSections(sections).reduce((total, section: any) => total + (Array.isArray(section?.fields) ? section.fields.length : 0), 0)

const resolveSectionsForSubmit = (form: any) => {
  const draftSections = normalizeSections(latestSectionDraft)
  const currentSections = normalizeSections(form.sections)
  if (!draftSections.length) return currentSections
  if (!currentSections.length) return draftSections
  return countSectionFields(currentSections) > countSectionFields(draftSections) ? currentSections : draftSections
}

const sectionsToItems = (sectionsRaw: any[], allowTitles?: string[]) => {
  const sections = normalizeSections(sectionsRaw)
  const allowList =
    Array.isArray(allowTitles) && allowTitles.length
      ? allowTitles
      : Array.isArray((sectionsRaw as any)?.__visibleTitles) && (sectionsRaw as any).__visibleTitles.length
        ? (sectionsRaw as any).__visibleTitles
        : []
  const items: any[] = []
  let order = 1
  sections
    .filter((s: any) => s && s.enabled !== false)
    .filter((s: any) => !allowList.length || allowList.includes(s.title || s.name || ''))
    .forEach((sec: any) => {
      const title = sec.title || sec.name || ''
      const cost_category = titleToCostCategory[title] || '1'
      ;(sec.fields || []).forEach((f: any) => {
        items.push({
          cost_category,
          item_order: order++,
          item_no: f.key || '',
          item_name_cn: f.nameCn || f.label || '',
          item_name_en: f.nameEn || '',
          item_name_vn: f.nameVn || '',
          is_fixed: f.fixed ? 1 : 0,
          is_computed: f.autoFill ? 1 : 0,
          purchaser_required: f.autoFill ? 0 : f.purchaserRequired ? 1 : 0,
          supplier_required: getSupplierRequiredCode(f),
          remark: f.remark || ''
        })
      })
    })
  return items
}

const itemsToSections = (items: any[], head?: any) => {
  const grouped = new Map<string, any[]>()
  ;(items || []).forEach((it: any) => {
    const title = costCategoryToTitle[String(it.cost_category ?? '')] || '其它成本'
    if (!grouped.has(title)) grouped.set(title, [])
    grouped.get(title)!.push(it)
  })
  const defaults = buildDefaultSections(head?.procurement_category)
  defaults.forEach((sec: any) => {
    const title = sec.title
    const rows = grouped.get(title) || []
    if (rows.length) {
      sec.enabled = true
      sec.fields = rows
        .slice()
        .sort((a: any, b: any) => (a.item_order || 0) - (b.item_order || 0))
        .map((r: any) => ({
          id: r.id,
          key: r.item_no,
          label: r.item_name_cn,
          nameCn: r.item_name_cn,
          nameEn: r.item_name_en,
          nameVn: r.item_name_vn,
          fixed: Number(r.is_fixed ?? r.item_category ?? 0) === 1,
          autoFill: Number(r.is_computed || 0) === 1,
          purchaserRequired: Number(r.is_computed || 0) === 1 ? false : Number(r.purchaser_required || 0) === 1,
          supplierRequiredCode: Number(r.supplier_required || 0) || 0,
          supplierBehavior: normalizeSupplierBehavior(
            Number(r.is_computed || 0) === 1 ? '' : r.supplier_behavior ?? r.supplier_required,
            Number(r.is_computed || 0) === 1 ? false : Number(r.purchaser_required || 0) === 1
          ),
          supplierRequired: Number(r.is_computed || 0) === 1 ? false : [1, 2, 5].includes(Number(r.supplier_required || 0)),
          remark: r.remark || '',
          builtIn: false
        }))
    }
    if (title === '材料成本') sec.supplierCanAddRow = Number(head?.is_can_add_materials || 0) === 1
    if (title === '加工成本') sec.supplierCanAddRow = Number(head?.is_can_add_process || 0) === 1
  })
  const allowedTitles = visibleTitles(head?.procurement_category, (head?.is_bom || 'Y') === 'Y')
  applyEnabledFlags(defaults, allowedTitles)
  return defaults
}

export const createCrudOptions = function ({ context }: CreateCrudOptionsProps): CreateCrudOptionsRet {
  return {
    crudOptions: {
      form: {
        labelWidth: '96px',
        col: { span: 12 },
        wrapper: {
          is: 'el-dialog',
          width: '95vw',
          top: '5vh'
        },
        group: {
          type: 'tab',
          base: {
            label: '基础信息',
            columns: ['template_name', 'procurement_category', 'template_desc']
          },
          controls: {
            label: '启用设置',
            columns: ['acti', 'is_bom']
          },
          sections: {
            label: '成本结构',
            columns: ['sections']
          }
        },
        async onOpened(ctx: any) {
          if (ctx.mode === 'add') {
            ctx.form.procurement_category = '2'
            ctx.form.is_bom = 'Y'
            ctx.form.acti = 'Y'
            refreshSectionsIfNeeded(ctx.form)
            latestSectionDraft = normalizeSections(ctx.form.sections)
            return
          }
          // 查看/编辑时：列表行可能不包含 items，强制拉详情回填，避免 sections/items 不同步导致页面展示不完整
          if ((ctx.mode === 'edit' || ctx.mode === 'view') && ctx.form?.id) {
            try {
              const res: any = await api.GetObj(ctx.form.id)
              const detail = res?.data?.data || res?.data || res
              if (detail && typeof detail === 'object') {
                Object.assign(ctx.form, detail)
                if (Array.isArray(detail.items)) {
                  const secs = itemsToSections(detail.items, detail)
                  const vis = visibleTitles(detail.procurement_category, (detail.is_bom || 'Y') === 'Y')
                  ;(secs as any).__visibleTitles = vis
                  ctx.form.sections = secs
                  ctx.form.__visibleTitles = vis
                  latestSectionDraft = normalizeSections(secs)
                }
              }
            } catch (e) {
              console.warn('加载成本模板详情失败', e)
            }
          }
        },
      },
      request: {
        pageRequest: async (query) => api.GetList(query),
        addRequest: async ({ form }) => {
          const sections = resolveSectionsForSubmit(form)
          const allowTitles = visibleTitles(form.procurement_category, (form.is_bom || 'Y') === 'Y')
          const payload: any = {
            template_no: form.template_no || undefined,
            template_name: form.template_name,
            procurement_category: form.procurement_category,
            is_bom: form.is_bom || 'Y',
            acti: form.acti || 'Y',
            template_desc: form.template_desc || '',
            is_can_add_materials: Number(sections.find((s: any) => s?.title === '材料成本')?.supplierCanAddRow) ? 1 : 0,
            is_can_add_process: Number(sections.find((s: any) => s?.title === '加工成本')?.supplierCanAddRow) ? 1 : 0,
            items: sectionsToItems(sections, allowTitles)
          }
          const categoryStats = payload.items.reduce((acc: Record<string, number>, item: any) => {
            const key = String(item.cost_category || '')
            acc[key] = (acc[key] || 0) + 1
            return acc
          }, {})
          const computedStats = payload.items.map((item: any) => ({
            cost_category: item.cost_category,
            item_no: item.item_no,
            is_computed: item.is_computed
          }))
          console.log('[CostTemplate] add payload.items stats', { total: payload.items?.length || 0, categories: categoryStats, allowTitles })
          console.log('[CostTemplate] add payload.items computed', computedStats)
          return api.AddObj(payload)
        },
        editRequest: async ({ form, row }) => {
          const sections = resolveSectionsForSubmit(form)
          const allowTitles = visibleTitles(form.procurement_category, (form.is_bom || 'Y') === 'Y')
          const payload: any = {
            id: row.id,
            template_no: form.template_no || row.template_no,
            template_name: form.template_name,
            procurement_category: form.procurement_category,
            is_bom: form.is_bom || 'Y',
            acti: form.acti || 'Y',
            template_desc: form.template_desc || '',
            is_can_add_materials: Number(sections.find((s: any) => s?.title === '材料成本')?.supplierCanAddRow) ? 1 : 0,
            is_can_add_process: Number(sections.find((s: any) => s?.title === '加工成本')?.supplierCanAddRow) ? 1 : 0,
            items: sectionsToItems(sections, allowTitles)
          }
          const categoryStats = payload.items.reduce((acc: Record<string, number>, item: any) => {
            const key = String(item.cost_category || '')
            acc[key] = (acc[key] || 0) + 1
            return acc
          }, {})
          const computedStats = payload.items.map((item: any) => ({
            cost_category: item.cost_category,
            item_no: item.item_no,
            is_computed: item.is_computed
          }))
          console.log('[CostTemplate] edit payload.items stats', { total: payload.items?.length || 0, categories: categoryStats, allowTitles })
          console.log('[CostTemplate] edit payload.items computed', computedStats)
          return api.UpdateObj(payload)
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
        fixed: 'right',
        minWidth: 220,
        buttons: {
          view: {
            show: true
          }
        }
      },
      columns: {
        template_name: {
          title: '模板名称',
          type: 'input',
          search: {
            show: true,
            component: {
              props: { placeholder: '请输入模板名称', clearable: true }
            }
          },
          form: {
            col: { span: 12 },
            rules: [{ required: true, message: '请输入模板名称' }]
          },
          column: { minWidth: 160 }
        },
        template_no: {
          title: '模板编号',
          type: 'input',
          search: {
            show: true,
            component: { props: { placeholder: '模板编号', clearable: true } }
          },
          form: { show: false },
          column: { width: 160, showOverflowTooltip: true }
        },
        procurement_category: {
          title: '采购类别',
          type: 'dict-select',
          dict: dict({ data: procurementDict }),
          column: { width: 120 },
          search: { show: true },
          form: {
            col: { span: 12 },
            value: '2',
            rules: [{ required: true, message: '请选择采购类别' }],
            valueChange({ form, value }) {
              refreshSectionsIfNeeded(form, { procurement_category: value })
              logPT('onChange procurement_category', value, { visibleTitles: form.__visibleTitles })
              logPT('sections titles now', Array.isArray(form.sections) ? form.sections.map((s: any) => s.title) : [])
            }
          },
          editForm: {
            component: { props: { disabled: true } }
          }
        },
        acti: {
          title: '有效',
          type: 'dict-select',
          dict: dict({ data: [
            { value: 'Y', label: '是' },
            { value: 'N', label: '否' }
          ] }),
          column: { width: 90 },
          search: { show: true },
          form: { value: 'Y' }
        },
        is_bom: {
          title: '启用BOM',
          type: 'dict-select',
          dict: dict({ data: [
            { value: 'Y', label: '是' },
            { value: 'N', label: '否' }
          ] }),
          column: { width: 100 },
          search: { show: true },
          form: {
            value: 'Y',
            valueChange({ form, value }) {
              refreshSectionsIfNeeded(form, { enable_cost_structure: value === 'Y' })
              logPT('onChange is_bom', value, { visibleTitles: form.__visibleTitles })
              logPT('sections titles now', Array.isArray(form.sections) ? form.sections.map((s: any) => s.title) : [])
            }
          }
        },
        template_desc: {
          title: '备注',
          type: 'textarea',
          column: { minWidth: 180, showOverflowTooltip: true },
          form: {
            col: { span: 12 },
            component: { props: { rows: 2 } }
          }
        },
        sections: {
          title: '',
          type: 'text',
          column: { show: false },
          form: {
            label: '',
            labelWidth: '0px',
            component: {
              name: SectionBuilder,
              props: {
                hideTitle: true,
                showTitleInput: false,
                defaultSections: buildDefaultSections('2'),
                visibleTitles: [],
                onDraftChange: (sections: any[]) => {
                  latestSectionDraft = normalizeSections(sections)
                }
              }
            },
            value: () => {
              const vis = visibleTitles('2', true)
              const defaults = ensureAllSections({ sections: buildDefaultSections('2') }, vis, '2')
              ;(defaults as any).__visibleTitles = vis
              return defaults
            },
            col: { span: 24 },
            itemProps: { labelWidth: 0, class: 'fc-section-item' },
            wrapper: { class: 'price-template-fs-dialog' }
          },
          valueBuilder({ form }) {
            // 编辑态优先以后端返回的 Body 明细(items) 还原 UI，不能再回退到默认 sections，
            // 否则会把数据库里的 is_computed 等真实值覆盖成前端预设默认值。
            if (Array.isArray(form.items) && form.items.length) {
              const secs = itemsToSections(form.items, form)
              const vis = visibleTitles(form.procurement_category, (form.is_bom || 'Y') === 'Y')
              ;(secs as any).__visibleTitles = vis
              form.sections = secs
              form.__visibleTitles = vis
              latestSectionDraft = normalizeSections(secs)
              logPT('valueBuilder(items)', { visibleTitles: form.__visibleTitles, sections: form.sections?.length, items: form.items.length })
              return
            }
            const vis = visibleTitles(form.procurement_category, (form.is_bom || 'Y') === 'Y')
            const ensured = ensureAllSections(form, vis, form.procurement_category)
            ;(ensured as any).__visibleTitles = vis
            form.sections = ensured
            form.__visibleTitles = vis
            latestSectionDraft = normalizeSections(ensured)
            logPT('valueBuilder', { visibleTitles: form.__visibleTitles, sections: form.sections?.length })
          },
          valueResolve({ form }) {
            // cost_template 返回的是 items，需要转换为 sections 供 UI 编辑
            if (Array.isArray(form.items) && form.items.length) {
              const secs = itemsToSections(form.items, form)
              const vis = visibleTitles(form.procurement_category, (form.is_bom || 'Y') === 'Y')
              ;(secs as any).__visibleTitles = vis
              form.sections = secs
              form.__visibleTitles = vis
              latestSectionDraft = normalizeSections(secs)
              return
            }
            const ensured = ensureAllSections(form, form.__visibleTitles || [], form.procurement_category)
            form.sections = ensured
            latestSectionDraft = normalizeSections(ensured)
            logPT('valueResolve', { sections: form.sections?.length })
          }
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
