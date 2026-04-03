import { compute, dict, CreateCrudOptionsProps, CreateCrudOptionsRet } from '@fast-crud/fast-crud'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as api from './api'

const statusDict = [
  { value: 1, label: '开立' },
  { value: 2, label: '确认' },
  { value: 3, label: '发布' },
  { value: 4, label: '报价中' },
  { value: 5, label: '报价结束' },
  { value: 6, label: '比议价中' },
  { value: 7, label: '价格审核' },
  { value: 8, label: '核价通过(结束)' },
  { value: 9, label: '落标(结束)' },
  { value: 0, label: '作废' }
]

const buyingMethodDict = [
  { value: 1, label: '询价' },
  { value: 2, label: '招标' }
]

const paymentMethods = [
  { value: 1, label: '月结30天' },
  { value: 2, label: '月结60天' },
  { value: 3, label: '不到付款' },
  { value: 4, label: '预付30%' },
  { value: 5, label: '预付50%' },
  { value: 6, label: '余款至生产' },
  { value: 7, label: '价格审核' },
  { value: 8, label: '价格结算(运费)' },
  { value: 9, label: '新建(结束)' }
]

const formatQuoteDeadlineDisplay = (value: unknown) => {
  if (!value) return ''
  const text = String(value).trim()
  if (!text) return ''
  const withMin = text.match(/^(\d{4}-\d{2}-\d{2})[ T](\d{2}):(\d{2})/)
  if (withMin) {
    return `${withMin[1]} ${withMin[2]}:${withMin[3]}`
  }
  const dateOnly = text.match(/^(\d{4}-\d{2}-\d{2})$/)
  if (dateOnly) {
    return `${dateOnly[1]} 00:00`
  }
  return text
}

export const normalizeDict = (value: unknown, label: string) => {
  if (value === null || value === undefined || value === '') return {}
  if (typeof value === 'string') {
    const parsed = JSON.parse(value)
    if (parsed === null || typeof parsed !== 'object' || Array.isArray(parsed)) {
      throw new Error(`${label} 需为 JSON 对象`)
    }
    return parsed
  }
  if (typeof value === 'object') return value as Record<string, unknown>
  throw new Error(`${label} 需为 JSON 对象`)
}

type ExtraHooks = {
  onAdd?: () => void
  onEdit?: (row: any) => void
  onView?: (row: any) => void
  /**
   * 跳转杂采比价/议价路由页（`/pisadmin/miscprocurement/rfqmiscellaneous/comparePrice/:id`；比议价中、价格审核、核价通过等由页内按钮状态控制）。
   * 比价页表头供应商名称可点击，进入报价单详情（`/pissupplier/quotation/detail/:id`，查看模式）。
   */
  onComparison?: (row: any) => void
  /** 列表多选变化（用于后续多询价单比价等） */
  onTableSelectionChange?: (rows: any[]) => void
  /** 与勾选列同步：由页面 ref 维护当前选中行，工具栏按钮据此取行（fast-crud 的 tableRef 往往拿不到 selection） */
  getTableSelection?: () => any[]
}

const STATUS_OPEN = 1
const STATUS_CONFIRMED = 2
const STATUS_PUBLISHED = 3
const STATUS_QUOTING = 4
const STATUS_QUOTING_ENDED = 5
const STATUS_BARGaining = 6
const STATUS_NEGOTIATED = 7
const STATUS_PRICE_AUDITED = 8
const STATUS_FINISHED = 9
const STATUS_CANCELLED = 0

/** 询价单接口错误文案：将数据库唯一约束等转为可读提示 */
export const formatRfqApiErrorMessage = (err: any, fallback: string) => {
  const d = err?.response?.data
  const pick = () => {
    if (typeof d?.msg === 'string' && d.msg.trim()) return d.msg
    if (typeof d?.message === 'string' && d.message.trim()) return d.message
    if (typeof d?.detail === 'string' && d.detail.trim()) return d.detail
    if (Array.isArray(d?.non_field_errors) && d.non_field_errors.length) return String(d.non_field_errors[0])
    return ''
  }
  const raw = pick() || (typeof err?.msg === 'string' ? err.msg : '') || (typeof err?.message === 'string' ? err.message : '')
  const s = typeof raw === 'string' ? raw : String(raw)
  if (
    /重复键违反唯一约束|unique constraint|UniqueViolation|duplicate key|already exists|pis_proc_inquiry_supplie/i.test(
      s
    )
  ) {
    if (/supplier|suppli|PartId|part_id|inquiry_no/i.test(s)) {
      return '供应商名单重复：同一询价单、同一料号下不能添加相同供应商，请删除重复行或更换供应商后再保存'
    }
    return '保存失败：存在与数据库冲突的重复数据，请检查供应商名单或其它唯一项'
  }
  if (s) return s.length > 280 ? `${s.slice(0, 280)}…` : s
  return fallback
}

const getRowStatus = (row: any) => Number(row?.status)
const isOpenStatus = (row: any) => getRowStatus(row) === STATUS_OPEN
const isConfirmedStatus = (row: any) => getRowStatus(row) === STATUS_CONFIRMED
const canPublishStatus = (row: any) => isConfirmedStatus(row)
/** 报价中(4)、报价结束(5) 可开启比价 */
// const isQuotingOrEndedStatus = (row: any) => [4, 5].includes(getRowStatus(row))
/** 改为仅状态：报价结束(5) 可开启比价 */
const isQuotingOrEndedStatus = (row: any) => getRowStatus(row) === STATUS_QUOTING_ENDED
/** 比议价中(6)、价格审核(7)、核价通过(8) 可打开比价窗口 */
const canOpenComparison = (row: any) => [6, 7, 8].includes(getRowStatus(row))
const getErrorMessage = (err: any, fallback: string) => formatRfqApiErrorMessage(err, fallback)

/** 列表行含 `suppliers` 时可先做提示；未返回嵌套时交由接口校验 */
const rowHasSuppliersList = (row: any): boolean | null => {
  const list = row?.suppliers
  if (!Array.isArray(list)) return null
  return list.length > 0
}

/** 成本模板版本号展示（不做位数补零） */
export const formatCostTemplateVersion = (v: unknown) => {
  if (v == null || v === '') return ''
  const n = Number(v)
  if (!Number.isFinite(n)) return String(v).trim()
  return String(Math.trunc(n))
}

/** 数据库数值型空值：展示 0.00（含占位符 -） */
export const displayNumericEmpty = (v: unknown): string => {
  if (v === null || v === undefined || v === '' || v === '-') return '0.00'
  const n = Number(v)
  if (Number.isFinite(n)) return n.toFixed(2)
  const s = String(v).trim()
  return s === '' ? '0.00' : s
}

/** 文本型空值：展示 - */
export const displayTextEmpty = (v: unknown): string => {
  if (v === null || v === undefined) return '-'
  const s = String(v).trim()
  return s === '' ? '-' : s
}

/** 利润率、税率等：空值 0.00%，数值保留两位小数并加 % */
export const displayPercentRate = (v: unknown): string => {
  if (v === null || v === undefined || v === '') return '0.00%'
  const raw = String(v).trim()
  if (raw === '') return '0.00%'
  const stripped = raw.replace(/%/g, '').trim()
  const n = Number(stripped)
  if (Number.isFinite(n)) return `${n.toFixed(2)}%`
  return raw.endsWith('%') ? raw : '0.00%'
}

/**
 * 比价「利润」行括号内展示：与 `QuotationProfit.profit_rate`（利润率）一致。
 * 值在 (0,1) 时按小数理解（如 0.03 → 3.00%），否则按百分数值（如 1 或 3 → 1.00% / 3.00%）。
 */
export const formatQuotationProfitMarginForCompare = (raw: unknown): string => {
  if (raw === null || raw === undefined || raw === '') return ''
  const n = Number(raw)
  if (!Number.isFinite(n)) return ''
  const pct = n > 0 && n < 1 ? n * 100 : n
  return `${pct.toFixed(2)}%`
}

/** 比价展开明细：与模板 fields 顺序一致 */
export type ComparisonDetailMetric = {
  label: string
  get: (r: any) => unknown
  isText: boolean
  /** 成本模板字段 key；用于跳过与分组标题重复的「材质 / 工站」行 */
  fieldKey?: string
}

/** 采购端比价页展开：不读成本模板，材料每组固定三行（与制程最低价列逻辑 fieldKey 对齐） */
export const COMPARE_PRICE_MATERIAL_DETAIL_METRICS: ComparisonDetailMetric[] = [
  { label: '重量', get: (r) => r?.weight, isText: false, fieldKey: 'weight' },
  { label: '单价', get: (r) => r?.unit_price ?? r?.unitPrice, isText: false, fieldKey: 'unitprice' },
  { label: '材料费用', get: (r) => r?.material_cost, isText: false, fieldKey: 'materialcost' }
]

/** 采购端比价页展开：加工每组固定一行「加工费」 */
export const COMPARE_PRICE_PROCESS_DETAIL_METRICS: ComparisonDetailMetric[] = [
  { label: '加工费', get: (r) => r?.process_price ?? r?.processPrice, isText: false, fieldKey: 'processprice' }
]

/** 比价展开：模板字段 key 归一化（与 index.vue 聚合逻辑共用） */
export const normCmpTplKey = (k: string) =>
  String(k || '')
    .trim()
    .toLowerCase()
    .replace(/_/g, '')

const toSnake = (s: string) =>
  String(s || '')
    .replace(/([A-Z])/g, '_$1')
    .replace(/^_/, '')
    .toLowerCase()

const materialGetterByNormKey: Record<string, (r: any) => unknown> = {
  material: (r) => r?.material_spec ?? r?.material,
  length: (r) => r?.length,
  width: (r) => r?.width,
  height: (r) => r?.height,
  specificgravity: (r) => r?.specific_gravity ?? r?.specificgravity,
  qty: (r) => r?.qty,
  quantity: (r) => r?.qty,
  weight: (r) => r?.weight,
  unitprice: (r) => r?.unit_price ?? r?.unitPrice,
  materialcost: (r) => r?.material_cost,
  lossrate: (r) => r?.loss_rate ?? r?.lossRate,
  remark: (r) => r?.remark,
  unit: (r) => r?.unit
}

const processGetterByNormKey: Record<string, (r: any) => unknown> = {
  processstation: (r) => r?.process_station,
  unit: (r) => r?.unit,
  unitrate: (r) => r?.unit_rate ?? r?.unitRate,
  processqty: (r) => r?.process_qty ?? r?.processQty,
  processprice: (r) => r?.process_price ?? r?.processPrice,
  processtime: (r) => r?.process_time ?? r?.processTime,
  remark: (r) => r?.remark,
  unitprice: (r) => r?.unit_rate ?? r?.unit_price,
  processcost: (r) => r?.process_price,
  lossrate: (r) => r?.loss_rate ?? r?.lossRate,
  cavitycount: (r) => r?.cavity_count ?? r?.cavityCount
}

const materialTextNormKeys = new Set(['material', 'remark', 'unit'])
const processTextNormKeys = new Set(['processstation', 'unit', 'remark'])

function fallbackRowGetter(rawKey: string): (r: any) => unknown {
  const k = String(rawKey || '').trim()
  return (r: any) => {
    if (r == null) return undefined
    const nk = normCmpTplKey(k)
    return r[k] ?? r[toSnake(k)] ?? r[nk]
  }
}

/** 材料成本：按成本模板 fields 顺序生成展开行 */
export function buildMaterialComparisonMetricsFromTemplateFields(fields: Array<{ key?: string; label?: string; nameCn?: string; name_cn?: string }>): ComparisonDetailMetric[] {
  const out: ComparisonDetailMetric[] = []
  if (!Array.isArray(fields)) return out
  for (const f of fields) {
    const rawKey = String(f?.key ?? '').trim()
    if (!rawKey) continue
    const nk = normCmpTplKey(rawKey)
    const label =
      String(f.label || f.nameCn || f.name_cn || '').trim() || rawKey
    const getter = materialGetterByNormKey[nk] ?? fallbackRowGetter(rawKey)
    const isText = materialTextNormKeys.has(nk)
    out.push({ label, get: getter, isText, fieldKey: rawKey })
  }
  return out
}

/** 加工成本：按成本模板 fields 顺序生成展开行 */
export function buildProcessComparisonMetricsFromTemplateFields(fields: Array<{ key?: string; label?: string; nameCn?: string; name_cn?: string }>): ComparisonDetailMetric[] {
  const out: ComparisonDetailMetric[] = []
  if (!Array.isArray(fields)) return out
  for (const f of fields) {
    const rawKey = String(f?.key ?? '').trim()
    if (!rawKey) continue
    const nk = normCmpTplKey(rawKey)
    const label =
      String(f.label || f.nameCn || f.name_cn || '').trim() || rawKey
    const getter = processGetterByNormKey[nk] ?? fallbackRowGetter(rawKey)
    const isText = processTextNormKeys.has(nk)
    out.push({ label, get: getter, isText, fieldKey: rawKey })
  }
  return out
}

/** 按材质规格分组后，不再展示「材质」行（与分组标题重复） */
export function shouldSkipMaterialDetailMetric(fieldKey: string | undefined): boolean {
  if (!fieldKey?.trim()) return false
  return normCmpTplKey(fieldKey) === 'material'
}

/** 按工站分组后，不再展示「加工工站」行（与分组标题重复） */
export function shouldSkipProcessDetailMetric(fieldKey: string | undefined): boolean {
  if (!fieldKey?.trim()) return false
  return normCmpTplKey(fieldKey) === 'processstation'
}

/** 制程最低价列：重量/单价行跳转目标 */
export type CompareMinLink =
  | { kind: 'quotation'; id: string | number }
  /** 杂采材料单价更低时链向杂采材料管理；sourceFactory 为对应「交易厂区」文案，供浮窗展示 */
  | { kind: 'misc_materials'; sourceFactory?: string }
  /** 主表「材料成本」：最低重量与最低单价来自不同报价单（或单价来自杂采材料信息）时，仅展示浮窗说明，不跳转 */
  | {
      kind: 'material_cost_split'
      weight: number
      unitPrice: number
      weightSource: string
      unitPriceSource: string
    }

/** 与后端制程最低价落库一致：全报价最低重量/最低单价（单价含杂采材料信息）、材料费=三者乘积；加工费=各报价单加工费合计之最小值 */
export type LowPriceMinContext = {
  minW?: number
  minUp?: number
  materialProduct?: number
  minProcessTotal?: number
  pid: string
  /** 全报价中材料明细最低重量所在报价单主键 */
  minWeightQuotationId?: string | number
  /** 全报价中材料明细最低单价所在报价单主键（若最低单价由杂采材料信息决定则为空） */
  minUnitPriceQuotationId?: string | number
  /** 仅当杂采单价严格低于所有报价单价时，单价/材料成本链向杂采材料管理；与报价持平或更高则链向报价单 */
  minUnitPriceFromMisc?: boolean
  /** 杂采材料最低价对应交易厂区（与杂采材料表 factory 等字段一致，供浮窗） */
  miscMinFactory?: string
}

const _nearlyEqualMin = (a: number, b: number) => Math.abs(a - b) < 1e-6

/** 各供应商列数值完全一致时，制程最低价列不展示超链接（仅纯文本） */
export function allCompareSupplierValuesEqual(
  values: Record<string, any>,
  supplierKeys: string[]
): boolean {
  if (!supplierKeys.length) return true
  const nums: number[] = []
  for (const k of supplierKeys) {
    const v = values[k]
    if (v === '-' || v === '' || v == null) return false
    const n = Number(v)
    if (!Number.isFinite(n)) return false
    nums.push(n)
  }
  if (nums.length !== supplierKeys.length) return false
  const a0 = nums[0]!
  return nums.every((x) => _nearlyEqualMin(x, a0))
}

export function computeLowPriceMinContext(
  quotes: any[],
  miscMinUnitPrice?: number | null,
  miscMinFactory?: string | null
): LowPriceMinContext {
  const pid = String(quotes[0]?.rfq_items?.[0]?.part_id || '').trim()
  const qty = Number(quotes[0]?.rfq_items?.[0]?.qty)
  let minW: number | undefined
  /** 各报价单材料行单价之最小值（不含杂采） */
  let minQuoteUp: number | undefined
  let minWeightQuotationId: string | number | undefined
  let minUnitPriceQuotationId: string | number | undefined
  const qid = (q: any) => q?.autoid ?? q?.id

  for (const q of quotes) {
    for (const r of q.material_costs || []) {
      if (pid && String(r.part_id || '').trim() !== pid) continue
      const w = Number(r.weight)
      if (Number.isFinite(w)) {
        if (minW === undefined || w < minW) {
          minW = w
          minWeightQuotationId = qid(q)
        }
      }
      const up = Number(r.unit_price)
      if (Number.isFinite(up)) {
        if (minQuoteUp === undefined || up < minQuoteUp) {
          minQuoteUp = up
          minUnitPriceQuotationId = qid(q)
        }
      }
    }
  }

  let minUp: number | undefined = minQuoteUp
  let minUnitPriceFromMisc = false
  let miscFactoryOut: string | undefined
  const pickMiscFactory = () => {
    const f = miscMinFactory != null && String(miscMinFactory).trim() !== '' ? String(miscMinFactory).trim() : ''
    if (f) miscFactoryOut = f
  }

  if (miscMinUnitPrice != null && Number.isFinite(miscMinUnitPrice)) {
    const misc = miscMinUnitPrice
    if (minQuoteUp === undefined) {
      minUp = misc
      minUnitPriceFromMisc = true
      minUnitPriceQuotationId = undefined
      pickMiscFactory()
    } else if (misc < minQuoteUp && !_nearlyEqualMin(misc, minQuoteUp)) {
      /** 仅当杂采单价严格低于所有报价单价时，制程最低价单价才记为来自杂采 */
      minUp = misc
      minUnitPriceFromMisc = true
      minUnitPriceQuotationId = undefined
      pickMiscFactory()
    } else {
      /** 杂采高于或与最低报价持平：取 min(报价最低, 杂采)，来源优先报价单（含持平） */
      minUp = Math.min(minQuoteUp, misc)
      minUnitPriceFromMisc = false
    }
  }
  let materialProduct: number | undefined
  if (minW !== undefined && minUp !== undefined && Number.isFinite(qty) && qty > 0) {
    materialProduct = minW * minUp * qty
  }
  let minProcessTotal: number | undefined
  for (const q of quotes) {
    let s = 0
    let ok = false
    for (const r of q.process_costs || []) {
      if (pid && String(r.part_id || '').trim() !== pid) continue
      const p = Number(r.process_price)
      if (Number.isFinite(p)) {
        s += p
        ok = true
      }
    }
    if (ok) minProcessTotal = minProcessTotal === undefined ? s : Math.min(minProcessTotal, s)
  }
  return {
    minW,
    minUp,
    materialProduct,
    minProcessTotal,
    pid,
    minWeightQuotationId,
    minUnitPriceQuotationId,
    minUnitPriceFromMisc,
    miscMinFactory: miscFactoryOut
  }
}

/** 主表「材料成本」制程最低价：同源则链向报价单详情，异源则链样式 + 浮窗说明分项来源 */
export function buildMaterialCostMinLink(
  ctx: LowPriceMinContext,
  quotes: any[],
  opts?: { materialRowValues?: Record<string, any>; supplierKeys?: string[] }
): CompareMinLink | null {
  const materialAllEqual =
    !!opts?.materialRowValues &&
    !!opts.supplierKeys?.length &&
    allCompareSupplierValuesEqual(opts.materialRowValues, opts.supplierKeys)

  /** 各报价一致且杂采单价严格低于所有报价：制程最低价指向杂采材料管理 */
  if (materialAllEqual && ctx.minUnitPriceFromMisc) {
    return {
      kind: 'misc_materials',
      sourceFactory: ctx.miscMinFactory
    }
  }
  if (materialAllEqual) {
    return null
  }
  if (ctx.materialProduct === undefined) return null
  const w = ctx.minW
  const up = ctx.minUp
  if (w === undefined || up === undefined || !Number.isFinite(w) || !Number.isFinite(up)) return null

  const wid = ctx.minWeightQuotationId
  const uid = ctx.minUnitPriceQuotationId
  const misc = ctx.minUnitPriceFromMisc

  const quoteLabel = (qid: string | number | undefined) => {
    if (qid == null || qid === '') return ''
    const q = quotes.find((x) => String(x.autoid ?? x.id) === String(qid))
    const name = String(q?.supplier_name || q?.supplierName || '').trim()
    const code = String(q?.supplier_code || q?.supplierCode || '').trim()
    const label = name || code
    return label || `报价单 #${qid}`
  }

  const weightSrc = quoteLabel(wid)
  const unitSrc = misc ? '杂采材料信息' : quoteLabel(uid)

  const sameQuotation =
    !misc && wid != null && wid !== '' && uid != null && uid !== '' && String(wid) === String(uid)

  if (sameQuotation) {
    return { kind: 'quotation', id: wid }
  }

  return {
    kind: 'material_cost_split',
    weight: w,
    unitPrice: up,
    weightSource: weightSrc || '—',
    unitPriceSource: unitSrc || '—'
  }
}

/** 展开仍按规格分行时，「制程最低价」列用全局口径覆盖该行 min */
export function applyMaterialDetailLowPriceMin(
  line: { min?: number; minLink?: CompareMinLink | null; values: Record<string, any> },
  m: ComparisonDetailMetric,
  ctx: LowPriceMinContext,
  supplierKeys?: string[]
): void {
  const fk = m.fieldKey ? normCmpTplKey(m.fieldKey) : ''
  const label = String(m.label || '').trim()
  if (ctx.minW !== undefined && (fk === 'weight' || /用量|重量/.test(label))) {
    line.min = ctx.minW
    const qid = ctx.minWeightQuotationId
    line.minLink =
      qid != null && qid !== ''
        ? { kind: 'quotation', id: qid }
        : null
    if (supplierKeys?.length && allCompareSupplierValuesEqual(line.values, supplierKeys)) {
      line.minLink = null
    }
    return
  }
  const isUnitPriceRow =
    fk === 'unitprice' || /材料单价/.test(label) || label === '单价'
  if (ctx.minUp !== undefined && isUnitPriceRow) {
    line.min = ctx.minUp
    if (ctx.minUnitPriceFromMisc) {
      line.minLink = {
        kind: 'misc_materials',
        sourceFactory: ctx.miscMinFactory
      }
    } else {
      const qid = ctx.minUnitPriceQuotationId
      line.minLink =
        qid != null && qid !== ''
          ? { kind: 'quotation', id: qid }
          : null
    }
    if (
      supplierKeys?.length &&
      allCompareSupplierValuesEqual(line.values, supplierKeys) &&
      !ctx.minUnitPriceFromMisc
    ) {
      line.minLink = null
    }
    return
  }
  if (ctx.materialProduct !== undefined && (fk === 'materialcost' || /材料费用|材料费/.test(label))) {
    line.min = ctx.materialProduct
    line.minLink = null
  }
}

/** 展开仍按工站分行时，「加工费用」行制程最低价为各报价单加工费合计的最小值 */
export function applyProcessDetailLowPriceMin(
  line: { min?: number },
  m: ComparisonDetailMetric,
  ctx: LowPriceMinContext
): void {
  const fk = m.fieldKey ? normCmpTplKey(m.fieldKey) : ''
  const label = String(m.label || '').trim()
  if (
    ctx.minProcessTotal !== undefined &&
    (fk === 'processprice' || fk === 'processcost' || /加工费|加工费用/.test(label))
  ) {
    line.min = ctx.minProcessTotal
  }
}

export const createCrudOptions = function ({
  context,
  crudExpose,
  onAdd,
  onEdit,
  onView,
  onComparison,
  onTableSelectionChange,
  getTableSelection
}: Partial<CreateCrudOptionsProps> & ExtraHooks): CreateCrudOptionsRet {
  void context

  const getSelectedRows = () => {
    if (typeof getTableSelection === 'function') {
      const rows = getTableSelection()
      if (Array.isArray(rows) && rows.length > 0) return rows
    }
    const expose = crudExpose as any
    // Element Plus：当前勾选行（与列表第一列选择列一致）
    const baseTable = expose?.getBaseTableRef?.()
    if (baseTable?.getSelectionRows) {
      const fromEl = baseTable.getSelectionRows()
      if (Array.isArray(fromEl) && fromEl.length) return fromEl
    }
    const tableRef: any = expose?.getTableRef?.() || expose?.tableRef
    const selection =
      tableRef?.getSelection?.() ||
      tableRef?.getSelectionRows?.() ||
      tableRef?.getSelections?.() ||
      tableRef?.getSelected?.() ||
      []
      if (Array.isArray(selection)) return selection
      return []  }

  /** 工具栏批量操作：取当前勾选的全部行（与列表选择列一致） */
  const pickSelectedRow = (): any | null => {
    const rows = getSelectedRows()
    if (!rows.length) {
      ElMessage.warning('请先选择询价单')
      return null
    }
    if (rows.length > 1) {
      ElMessage.warning('仅支持单条操作')
      return null
    }
    return rows[0]
  }

  return {
    crudOptions: {
      form: {
        labelWidth: '120px',
        col: { span: 12 },
        wrapper: { is: 'el-dialog', width: '960px', top: '6vh', title: '询价单' },
        group: {
          type: 'tab',
          base: { label: '基础信息', columns: ['code', 'title', 'product_category', 'template', 'part_no', 'part_name', 'quote_deadline', 'purchase_qty', 'buyer', 'currency', 'plant', 'target_price', 'lead_time_days', 'payment_term', 'status', 'remark'] },
          cost: { label: '成本结构', columns: ['cost_items'] },
          vendors: { label: '供应商名单', columns: ['vendors'] },
          attachments: { label: '附件', columns: ['attachments'] }
        }
      },
      request: {
        pageRequest: async (query) => api.GetList(query),
        // 新版：新增/编辑由 detail.vue 路由页负责（嵌套子表一次提交）
        addRequest: async ({ form }) => api.AddObj(form),
        editRequest: async ({ form, row }) => api.UpdateObj({ ...form, id: row.id }),
        delRequest: async ({ row }) => {
          try {
            return await api.DelObj(row.id)
          } catch (err: any) {
            ElMessage.error(getErrorMessage(err, '删除失败'))
            throw err
          }
        }
      },
      table: {
        rowKey: 'id',
        onSelectionChange: (changed: any[]) => {
          onTableSelectionChange?.(changed || [])
        }
      },
      actionbar: {
        buttons: {
          add: {
            show: true,
            text: '新建询价单',
            click() {
              onAdd && onAdd()
            }
          },
          startBargaining: {
            show: true,
            text: '开启比价',
            order: 2,
            type: 'warning',
            async click() {
              const row = pickSelectedRow()
              if (!row) return
              if (!isQuotingOrEndedStatus(row)) {
                ElMessage.warning('仅报价中或报价结束状态可开启比价')
                return
              }
              try {
                await ElMessageBox.confirm('确认将状态改为【比议价中】？', '提示', {
                  type: 'warning',
                  confirmButtonText: '确定',
                  cancelButtonText: '取消'
                })
                await api.StartBargainingObj(row.id)
                await api.SaveNegotiationRecordsObj(row.id, { records: [] })

                onComparison && onComparison(row)
                crudExpose?.doRefresh?.()
              } catch (err: any) {
                if (err === 'cancel' || err === 'close') return
                ElMessage.error(getErrorMessage(err, '开启比价失败'))
              }
            }
          },
        }
      },
      rowHandle: {
        fixed: 'right',
        width: 500,
        buttons: {
          view: { show: false },
          edit: { show: false },
          remove: {
            text: '删除',
            // 禁用时不沿用 danger 的淡红底，改为 info 灰底 + disabled
            type: compute(({ row }) => (isOpenStatus(row) ? 'danger' : 'info')),
            order: 1,
            show: true,
            disabled: compute(({ row }) => !isOpenStatus(row))
          },
          customView: {
            text: '查看',
            type: 'default',
            order: 0,
            show: true,
            click({ row }) {
              onView && onView(row)
            }
          },
          customEdit: {
            text: '编辑',
            type: compute(({ row }) => (isOpenStatus(row) ? 'primary' : 'info')),
            order: 1.5,
            show: true,
            disabled: compute(({ row }) => !isOpenStatus(row)),
            click({ row }) {
              if (!isOpenStatus(row)) return
              onEdit && onEdit(row)
            }
          },
          confirm: {
            text: '确认',
            type: compute(({ row }) => (isOpenStatus(row) ? 'success' : 'info')),
            order: 2,
            show: true,
            disabled: compute(({ row }) => !isOpenStatus(row)),
            async click({ row }) {
              if (!isOpenStatus(row)) return
              try {
                const supplierOk = rowHasSuppliersList(row)
                if (supplierOk === false) {
                  ElMessage.warning('请先维护询价单供应商名单后再确认')
                  return
                }
                await ElMessageBox.confirm('确认后，该询价单将锁定并不可再编辑。如需修改，后续需执行【还原】操作', '提示', {
                  type: 'warning',
                  confirmButtonText: '确定',
                  cancelButtonText: '取消'
                })
                const res = await api.ConfirmObj(row.id)
                crudExpose?.doRefresh?.()
                return res
              } catch (err: any) {
                if (err === 'cancel' || err === 'close') return
                ElMessage.error(getErrorMessage(err, '确认失败'))
                throw err
              }
            }
          },
          restore: {
            text: '还原',
            type: compute(({ row }) => (isConfirmedStatus(row) ? 'primary' : 'info')),
            order: 2.5,
            show: true,
            disabled: compute(({ row }) => !isConfirmedStatus(row)),
            async click({ row }) {
              if (!isConfirmedStatus(row)) return
              try {
                await ElMessageBox.confirm('确认将状态还原为【开立】？', '提示', {
                  type: 'warning',
                  confirmButtonText: '确定',
                  cancelButtonText: '取消'
                })
                const res = await api.RestoreObj(row.id)
                crudExpose?.doRefresh?.()
                return res
              } catch (err: any) {
                if (err === 'cancel' || err === 'close') return
                ElMessage.error(getErrorMessage(err, '还原失败'))
                throw err
              }
            }
          },
          publish: {
            text: '发布',
            type: compute(({ row }) => (canPublishStatus(row) ? 'warning' : 'info')),
            order: 3,
            show: true,
            disabled: compute(({ row }) => !canPublishStatus(row)),
            async click({ row }) {
              if (!canPublishStatus(row)) return
              try {
                await ElMessageBox.confirm('确认将状态改为【发布】？', '提示', {
                  type: 'warning',
                  confirmButtonText: '确定',
                  cancelButtonText: '取消'
                })
                const res = await api.PublishObj(row.id)
                crudExpose?.doRefresh?.()
                return res
              } catch (err: any) {
                if (err === 'cancel' || err === 'close') return
                ElMessage.error(getErrorMessage(err, '发布失败'))
                throw err
              }
            }
          },
          viewComparison: {
            text: '比价',
            type: compute(({ row }) => (canOpenComparison(row) ? 'primary' : 'info')),
            order: 0.25,
            show: true,
            disabled: compute(({ row }) => !canOpenComparison(row)),
            click({ row }) {
              if (!canOpenComparison(row)) return
              onComparison && onComparison(row)
            }
          }
        }
      },
      columns: {
        $checked: {
          title: '',
          form: { show: false },
          search: { show: false },
          column: {
            type: 'selection',
            align: 'center',
            width: 52,
            fixed: 'left',
            columnSetDisabled: true
          }
        },
        company_short_name: {
          title: '交易厂区',
          type: 'text',
          form: { show: false },
          search: { show: false },
          column: {
            minWidth: 100,
            showOverflowTooltip: true,
            formatter: ({ row }: { row: any }) => {
              const v = row?.company_short_name ?? row?.companyShortName
              return v != null && v !== '' ? String(v) : ''
            }
          }
        },
        buying_method: {
          title: '采购方式',
          type: 'dict-select',
          dict: dict({ data: buyingMethodDict }),
          search: {
            show: true,
            component: { props: { placeholder: '采购方式', clearable: true } }
          },
          form: { show: false },
          column: {
            width: 100,
            formatter: ({ row, value }: { row: any; value: unknown }) => {
              const v = value ?? row?.buying_method
              const n = Number(v)
              if (!Number.isFinite(n)) return v != null && v !== '' ? String(v) : ''
              return buyingMethodDict.find((d) => d.value === n)?.label ?? String(v)
            }
          }
        },
        inquiry_no: {
          title: '询价单号',
          type: 'input',
          search: {
            show: true,
            component: { props: { placeholder: '请输入询价单号', clearable: true } }
          },
          form: {
            show: false
          },
          column: { minWidth: 120, showOverflowTooltip: true }
        },
        title: {
          title: '询价单名称',
          type: 'input',
          search: {
            show: true,
            component: { props: { placeholder: '请输入询价单名称', clearable: true } }
          },
          form: { rules: [{ required: true, message: '请输入询价单名称' }] },
          column: { minWidth: 160, showOverflowTooltip: true }
        },
        template: {
          title: '询价模版',
          type: 'input',
          column: {
            minWidth: 120,
            showOverflowTooltip: true,
            formatter: ({ row, value }: { row: any; value: unknown }) => {
              const code = String(value ?? row?.template ?? row?.template_code ?? '').trim()
              const verRaw = row?.template_version ?? row?.templateVersion ?? row?.cost_template_version
              if (!code) return ''
              if (verRaw != null && verRaw !== '') return `${code}（V${formatCostTemplateVersion(verRaw)}）`
              return code
            }
          }
        },
        quote_deadline: {
          title: '报价截止时间',
          type: 'datetime',
          column: {
            width: 150,
            formatter: ({ value }: { value: unknown }) => formatQuoteDeadlineDisplay(value)
          }
        },
        bid_start_time: {
          title: '投标开始时间',
          type: 'datetime',
          column: {
            width: 150,
            formatter: ({ row, value }: { row: any; value: unknown }) =>
              Number(row?.buying_method) === 1 ? '-' : formatQuoteDeadlineDisplay(value)
          }
        },
        bid_end_time: {
          title: '投标截止时间',
          type: 'datetime',
          column: {
            width: 150,
            formatter: ({ row, value }: { row: any; value: unknown }) =>
              Number(row?.buying_method) === 1 ? '-' : formatQuoteDeadlineDisplay(value)
          }
        },
        buyer: {
          title: '采购负责人',
          type: 'input',
          search: {
            show: true,
            component: { props: { placeholder: '请输入采购负责人', clearable: true } }
          },
          form: { rules: [{ required: true, message: '请输入采购负责人' }] },
          column: { minWidth: 120 }
        },
        currency: {
          title: '币别',
          type: 'dict-select',
          dict: dict({ data: [
            { value: 'CNY', label: 'CNY' },
            { value: 'USD', label: 'USD' }
          ] }),
          column: { width: 100 },
          form: { value: 'CNY' }
        },
        lead_time_days: {
          title: '交货周期(天)',
          type: 'number',
          column: { width: 120 },
          form: { component: { props: { precision: 0 } } }
        },
        payment_method: {
          title: '付款方式',
          type: 'dict-select',
          dict: dict({ data: paymentMethods }),
          column: { width: 140, showOverflowTooltip: true },
          form: { show: false }
        },
        status: {
          title: '状态',
          type: 'dict-select',
          dict: dict({ data: statusDict }),
          column: { width: 140 }
        },
        remark: {
          title: '备注',
          type: 'textarea',
          column: { minWidth: 180, showOverflowTooltip: true },
          form: { component: { props: { rows: 3 } } }
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
