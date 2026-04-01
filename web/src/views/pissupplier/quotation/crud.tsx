import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import * as api from './api'
import * as inquiryApi from '../../pisadmin/miscprocurement/rfqmiscellaneous/api'
import { GetList as GetCostTemplateList } from '../../pisadmin/miscprocurement/cost_template/api'
import { GetList as GetMaterials } from '../../pisadmin/miscprocurement/misc_materials/api'
import { GetList as GetMiscParts } from '../../pisadmin/miscprocurement/misc_parts/api'
import { GetList as GetStations } from '../../pisadmin/miscprocurement/misc_stations/api'
import { GetList as GetUnits } from '../../pisadmin/basicinfo/unit/api'

/** 与 loadQuotes / openQuote 等处解析列表响应一致 */
const extractPagedList = (res: any): any[] => {
  const raw = res?.data?.results ?? res?.data?.data?.results ?? res?.data?.list ?? res?.data
  return Array.isArray(raw) ? raw : []
}

export type QuoteStatus = 'pending' | 'quoted' | 'completed' | 'expired'
type CostAttr = { key: string; label: string; value: string | number; type?: string }
type CostTemplateItem = { section: string; attrs: CostAttr[]; span?: 'wide'; allowAdd?: boolean }
type CostItem = { id: string; section: string; span?: 'wide'; attrs: CostAttr[]; field?: string }
type CostRow = {
  id: string
  section: string
  field: string
  values: Record<string, any>
  labels?: Record<string, string>
  /** 对应后端明细行 part_id，保存时写回 material_costs / process_costs 等 */
  partId?: string
}
type Quote = {
  id: string
  quoteNo: string
  inquiryCode: string
  inquiryTitle: string
  /** 询价主表 `Inquiry.company_code` */
  inquiryCompanyCode?: string
  /** 公司信息简称（交易厂区/询价厂区展示） */
  companyShortName?: string
  inquiryStatus: string
  /** 询价主表 `Inquiry.status`（数字），用于中标列与 status=9 判断 */
  inquiryStatusCode?: number | null
  /** 报价主表 `QuotationMaster.buying_method`（发布时自询价单拷贝） */
  buyingMethod?: number | null
  /** 报价主表投标时间（询价=1 时列表/表单显示「-」） */
  bidStartTime?: string
  bidEndTime?: string
  template: string
  currency: string
  /** 与后端 `quote_deadline`（DateTime）对应的展示用字符串，经 `formatQuoteDeadlineDisplay` 规范化 */
  quoteDeadline: string
  quoteAmount: string
  quoteTime: string
  status: QuoteStatus
  /** 后端 `QuotationMaster.status`：1 未报价 2 已报价 3 已过期（以后台库为准） */
  statusCode: number
  /** 后端 `is_awarded`：1 已中标 0 否 */
  isAwarded: number
  /** 与后端 QuotationMaster.supplier_code 一致，保存/提交时必须带回 */
  supplierCode: string
  supplierName: string
  base: {
    contact: string
    phone: string
    email: string
    validityDays: string
    leadTimeDays: string
    paymentTerm: string
  }
  costItems: CostItem[]
  /** 报价方上传的附件（`pis_sup_quotation_attachment`） */
  attachments: any[]
  /** 询价单关联附件（`pis_proc_inquiry_attachment`），详情接口 `inquiry_attachments` */
  inquiryAttachments: InquiryAttachmentRow[]
  remark: string
  createdAt: string
  templateSections?: any
  enableCostStructure?: boolean
  /** 详情接口返回的产品明细，保存时原样带回以不清空子表 */
  rfqItems?: any[]
}

type SummaryRow = { section: string; amount: number; isSubtotal?: boolean }

/** 与杂采询价列表列展示一致 */
export const buyingMethodDict = [
  { value: 1, label: '询价' },
  { value: 2, label: '招标' }
]

export function formatQuoteDeadlineDisplay(value: unknown) {
  if (!value) return ''
  const text = String(value).trim()
  if (!text) return ''
  // 匹配完整日期时间：yyyy-mm-dd HH:MM:SS 或 yyyy-mm-ddTHH:MM:SS
  const fullMatched = text.match(/^(\d{4}-\d{2}-\d{2})[ T](\d{2}):(\d{2})/)
  if (fullMatched) {
    return `${fullMatched[1]} ${fullMatched[2]}:${fullMatched[3]}`
  }
  // 匹配只到小时：yyyy-mm-dd HH
  const hourMatched = text.match(/^(\d{4}-\d{2}-\d{2})[ T](\d{2})/)
  if (hourMatched) {
    return `${hourMatched[1]} ${hourMatched[2]}:00`
  }
  // 只有日期：yyyy-mm-dd
  const dateOnly = text.match(/^(\d{4}-\d{2}-\d{2})$/)
  if (dateOnly) {
    return `${dateOnly[1]} 00:00`
  }
  return text
}

/** 将后端返回的 `quote_deadline`（ISO 或 `YYYY-MM-DD HH:mm:ss`）规范为列表/表单展示用字符串 */
export function normalizeQuoteDeadlineFromApi(value: unknown): string {
  return formatQuoteDeadlineDisplay(value)
}

/** 解析报价截止时间用于本地筛选（与 `YYYY-MM-DD HH:mm:ss` / ISO 字符串兼容） */
export function parseQuoteDeadlineToMs(value: unknown): number {
  if (value == null || value === '') return NaN
  const text = String(value).trim()
  if (!text) return NaN
  const normalized = formatQuoteDeadlineDisplay(text)
  if (!normalized) return NaN
  const forDate = normalized.replace(/^(\d{4}-\d{2}-\d{2})\s+/, '$1T')
  const d = new Date(forDate)
  const t = d.getTime()
  return Number.isNaN(t) ? NaN : t
}

/** 报价主表 `buying_method === 2`（招标） */
export function isBuyingMethodBidding(row: any) {
  return Number(row?.buyingMethod ?? row?.buying_method) === 2
}

/** 非招标不限制；招标须在投标开始～截止（含端点）内；缺时间则不可用 */
export function isWithinSupplierBidWindow(row: any, nowMs: number = Date.now()) {
  if (!isBuyingMethodBidding(row)) return true
  const start = parseQuoteDeadlineToMs(row?.bidStartTime ?? row?.bid_start_time)
  const end = parseQuoteDeadlineToMs(row?.bidEndTime ?? row?.bid_end_time)
  if (!Number.isFinite(start) || !Number.isFinite(end)) return false
  return nowMs >= start && nowMs <= end
}

/** 非招标或未超限返回 null；否则返回提示文案（列表按钮禁用、openQuote/submit 前置校验） */
export function getSupplierBidWindowRejectReason(row: any, nowMs: number = Date.now()): string | null {
  if (!isBuyingMethodBidding(row)) return null
  const start = parseQuoteDeadlineToMs(row?.bidStartTime ?? row?.bid_start_time)
  const end = parseQuoteDeadlineToMs(row?.bidEndTime ?? row?.bid_end_time)
  if (!Number.isFinite(start) || !Number.isFinite(end)) {
    return '招标项目缺少投标开始或截止时间，无法报价或提交'
  }
  if (nowMs < start) return '投标尚未开始，请在投标开始后再报价或提交'
  if (nowMs > end) return '已超过投标截止时间，无法报价或提交'
  return null
}

/**
 * 保存主表时提交 `quote_deadline`：后端为 DateTimeField，提交 `YYYY-MM-DD HH:mm:ss` 或省略
 */
export function quoteDeadlineToApiPayload(value: unknown): string | undefined {
  if (value == null || value === '') return undefined
  const raw = String(value).trim()
  if (!raw) return undefined
  const normalized = formatQuoteDeadlineDisplay(raw)
  if (!normalized) return undefined
  const m = normalized.match(/^(\d{4}-\d{2}-\d{2})\s+(\d{2}):(\d{2})(?::(\d{2}))?$/)
  if (m) {
    const sec = m[4] ?? '00'
    return `${m[1]} ${m[2]}:${m[3]}:${sec}`
  }
  const m2 = normalized.match(/^(\d{4}-\d{2}-\d{2})$/)
  if (m2) return `${m2[1]} 00:00:00`
  const isoCandidate = raw.includes('T') || raw.includes('Z') ? raw : raw.replace(/^(\d{4}-\d{2}-\d{2})\s+/, '$1T')
  const d = new Date(isoCandidate)
  if (Number.isNaN(d.getTime())) return undefined
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

/** 列表「投标开始/截止」列：采购方式=询价 时显示「-」 */
export function formatBidTimeColumn(row: any, value: unknown) {
  if (Number(row?.buyingMethod ?? row?.buying_method) === 1) return '-'
  return formatQuoteDeadlineDisplay(value)
}

export type InquiryAttachmentRow = {
  id?: number | string
  part_id?: string
  file_type?: number
  file_type_label?: string
  file_name?: string
  file_path?: string
  upload_time?: string
  upload_user?: string
}

/** 与 `pis_proc_inquiry_attachment` / 询价单 `attachments` 嵌套结构一致（勿用报价单 `attachments`） */
const INQUIRY_FILE_TYPE_LABELS: Record<number, string> = {
  1: '产品图纸',
  2: '招标文件',
  3: '其它文件'
}

export function mapInquiryAttachmentsFromInquiryApi(rows: any[] | null | undefined): InquiryAttachmentRow[] {
  if (!Array.isArray(rows) || !rows.length) return []
  return rows.map((r) => {
    const ft = Number(r.file_type)
    const t = ft === 1 || ft === 2 || ft === 3 ? ft : 3
    return {
      id: r.id,
      part_id: r.part_id,
      file_type: t,
      file_type_label: r.file_type_label || INQUIRY_FILE_TYPE_LABELS[t],
      file_name: r.file_name,
      file_path: r.file_path,
      upload_time: r.upload_time,
      upload_user: r.upload_user
    }
  })
}

/** el-upload 的 file-list → 后端 `QuotationAttachment` 行 */
function buildQuotationAttachmentsForSave(files: any[] | null | undefined, defaultPartId: string): any[] {
  if (!Array.isArray(files) || !files.length) return []
  const pid = String(defaultPartId || '').trim()
  const out: any[] = []
  for (const f of files) {
    const name = String(f?.name ?? f?.file_name ?? '').trim()
    const path = String(
      f?.url ?? f?.file_path ?? f?.response?.url ?? f?.response?.data?.url ?? f?.response?.data?.file ?? ''
    ).trim()
    if (!name && !path) continue
    out.push({
      part_id: String(f?.part_id ?? f?.partId ?? pid).trim() || pid,
      file_name: name,
      file_path: path || null
    })
  }
  return out
}

const unwrapUploadResponse = (res: any) => res?.data?.data ?? res?.data ?? res

/**
 * 新选文件仅有 `raw`，须先走 `/api/system/file/` 上传拿到路径（与询价单附件保存一致）。
 */
async function uploadQuotationAttachmentFile(fileItem: any) {
  const existing = String(fileItem?.url ?? fileItem?.file_path ?? '').trim()
  if (existing) {
    return {
      ...fileItem,
      url: existing,
      file_path: existing,
      status: 'success'
    }
  }
  const rawFile = fileItem?.raw
  if (!rawFile) {
    return { ...fileItem, url: '', file_path: '', status: fileItem?.status || 'ready' }
  }
  const formData = new FormData()
  formData.append('file', rawFile)
  formData.append('upload_method', '1')
  const res = await inquiryApi.UploadFile(formData)
  const uploaded = unwrapUploadResponse(res) || {}
  const filePath = String(uploaded.url || uploaded.file_url || '').trim()
  return {
    ...fileItem,
    name: fileItem?.name || uploaded.name || rawFile.name || '',
    url: filePath,
    file_path: filePath,
    status: 'success'
  }
}

/** 详情嵌套 `attachments`（file_name/file_path）→ el-upload `file-list` */
function normalizeQuotationAttachmentsForUpload(rows: any[] | null | undefined): any[] {
  if (!Array.isArray(rows) || !rows.length) return []
  return rows.map((r, i) => ({
    uid: r.uid ?? (r.autoid != null ? `a-${r.autoid}` : `ex-${i}`),
    name: r.name ?? r.file_name ?? '',
    url: r.url ?? r.file_path ?? '',
    part_id: r.part_id,
    status: r.status ?? 'success'
  }))
}

const statusOptions = [
  { label: '待报价', value: 'pending' },
  { label: '报价中', value: 'quoted' },
  { label: '已报价', value: 'completed' },
  { label: '已过期', value: 'expired' }
]

const statusMapBackendToFront: Record<number, QuoteStatus> = {
  1: 'pending',
  2: 'quoted',
  3: 'completed',
  4: 'expired'
}

const statusMapFrontToBackend: Record<QuoteStatus, number> = {
  pending: 1,
  quoted: 2,
  completed: 3,
  expired: 4
}

/**
 * 列表「中标状态」列：is_awarded + 报价 status + 询价 status
 * - is_awarded==1 → 文案「中标」+ 旗帜图标（由模板渲染）
 * - is_awarded==0 且 status==1 → 待报价
 * - is_awarded==0 且 status==2 → 报价中
 * - is_awarded==0 且 status==3 且询价 status!=9 → 评标中
 * - is_awarded==0 且 status==3 且询价 status==9 → 未中标
 * - status==4 → 空
 */
export function formatAwardBidStatus(row: {
  isAwarded?: number | string
  is_awarded?: number | string
  statusCode?: number | string
  status?: QuoteStatus
  inquiryStatusCode?: number | string | null
}): { mode: 'flag'; text: string } | { mode: 'text'; text: string } {
  const ia = Number(row.isAwarded ?? row.is_awarded ?? 0) === 1 ? 1 : 0
  let sc: number
  if (row.statusCode !== undefined && row.statusCode !== null && row.statusCode !== '') {
    sc = Number(row.statusCode)
  } else {
    sc = statusMapFrontToBackend[(row.status as QuoteStatus) || 'pending'] ?? 1
  }
  const inqRaw = row.inquiryStatusCode
  const inqNum = inqRaw === undefined || inqRaw === null || inqRaw === '' ? NaN : Number(inqRaw)

  if (sc === 4) return { mode: 'text', text: '' }
  if (ia === 1) return { mode: 'flag', text: '中标' }
  if (ia === 0 && sc === 1) return { mode: 'text', text: '待报价' }
  if (ia === 0 && sc === 2) return { mode: 'text', text: '报价中' }
  if (ia === 0 && sc === 3) {
    if (!Number.isFinite(inqNum)) return { mode: 'text', text: '评标中' }
    if (inqNum !== 9) return { mode: 'text', text: '评标中' }
    return { mode: 'text', text: '未中标' }
  }
  return { mode: 'text', text: '—' }
}

/** 与 `miscprocurement.Inquiry.STATUS_CHOICES` 一致 */
const MISC_INQUIRY_STATUS_LABELS: Record<number, string> = {
  1: '开立',
  2: '确认',
  3: '发布',
  4: '报价中',
  5: '报价结束',
  6: '比议价中',
  7: '价格审核',
  8: '核价通过(结束)',
  9: '落标(结束)',
  0: '作废'
}

/** 弹窗/列表：询价状态由数字转为文案；已是文案则原样返回 */
export function formatMiscInquiryStatus(row: {
  inquiryStatus?: string
  inquiryStatusCode?: number | string | null
}): string {
  const codeRaw = row.inquiryStatusCode
  if (codeRaw !== undefined && codeRaw !== null && codeRaw !== '') {
    const n = Number(codeRaw)
    if (Number.isFinite(n) && MISC_INQUIRY_STATUS_LABELS[n] != null) {
      return MISC_INQUIRY_STATUS_LABELS[n]
    }
  }
  const s = row.inquiryStatus == null ? '' : String(row.inquiryStatus).trim()
  if (s === '') return ''
  if (/^\d+$/.test(s)) {
    const n = Number(s)
    if (Number.isFinite(n) && MISC_INQUIRY_STATUS_LABELS[n] != null) {
      return MISC_INQUIRY_STATUS_LABELS[n]
    }
  }
  return s
}

const paymentMapFrontToBackend: Record<string, number> = {
  tt_30_70: 4,
  net30: 1,
  net45: 2,
  prepaid: 4
}

const paymentMapBackendToFront: Record<number, string> = {
  1: 'net30',
  2: 'net45',
  3: 'tt_30_70',
  4: 'tt_30_70'
}

/** 与报价基础信息 `paymentTerm` 选项一致，供详情页只读展示 */
export const PAYMENT_TERM_LABELS: Record<string, string> = {
  tt_30_70: 'T/T 30%预付，70%出货前',
  net30: '月结30天',
  net45: '月结45天',
  prepaid: '全额预付'
}

export function formatPaymentTermLabel(term: string | null | undefined) {
  if (term == null || String(term).trim() === '') return '—'
  const k = String(term).trim()
  return PAYMENT_TERM_LABELS[k] ?? k
}

const costEnabledSections = ['材料成本', '加工成本', '其它成本', '利润', '税金']
const costDisabledSections = ['产品明细', '利润', '税金']

const priceKeys = ['unitPrice', 'unitprice', 'price', 'unit_price']
const materialCalcKeys = ['length', 'len', 'width', 'height', 'specificgravity', 'unitPrice', 'unitprice', 'qty', 'quantity', 'num', 'count']
const specificGravityKeys = ['specificgravity', 'density', '比重']
const weightKeys = ['weight', '重量']
const materialFeeKeys = ['material_fee', 'materialFee', 'material_cost', 'materialCost', 'material_amount', 'materialAmount', '材料费用']
const lengthKeys = ['length', 'len', '长']
const widthKeysForCalc = ['width', '宽']
const heightKeys = ['height', '高']
const quantityKeys = ['qty', 'quantity', 'num', 'count', '数量']
const materialTotalKeys = ['materialTotal', 'material_total', '材料成本合计']
const processTotalKeys = ['processTotal', 'process_total', '加工成本合计']
const processUnitKeys = ['unit', 'process_unit', '单位']
const processRateKeys = ['unitrate', 'rate', 'process_rate', 'fee_rate']
const processQtyKeys = ['process_qty', 'processqty', 'qty', 'quantity', 'num', 'count']
const processFeeKeys = ['processFee', 'processprice', 'process_price', 'process_cost', 'process_fee', '加工费', 'fee']
const processStationKeys = ['process_station', 'processStation']

/**
 * 与后端子表模型字段及 costRowsToNestedPayload 使用的 row.values 键一致。
 * 展示用列名优先来自询价 `template_sections` 各段 `fields[].label`（与 miscInquiryDetail 成本结构一致），
 * 本常量仅在模板未配置字段时作列键与默认标题的 fallback。
 * QuotationMaterial / QuotationProcess / QuotationOther / QuotationProfit 见 apps.pissupplier.models
 */
export type QuotationCostColumn = {
  key: string
  label: string
}

export const FIXED_QUOTATION_SECTION_COLUMNS: Record<string, QuotationCostColumn[]> = {
  材料成本: [
    { key: 'material', label: '材质' },
    { key: 'len', label: '长(mm)' },
    { key: 'width', label: '宽(mm)' },
    { key: 'height', label: '高(mm)' },
    { key: 'specificgravity', label: '比重(kg/cm³)' },
    { key: 'qty', label: '数量' },
    { key: 'weight', label: '重量(kg)' },
    { key: 'unitPrice', label: '单价' },
    { key: 'material_fee', label: '材料费用' },
    { key: 'remark', label: '备注' }
  ],
  加工成本: [
    { key: 'processStation', label: '加工工站' },
    { key: 'processUnit', label: '单位' },
    { key: 'processRate', label: '费率' },
    { key: 'processMeasure', label: '加工计量' },
    { key: 'processFee', label: '加工费' },
    { key: 'remark', label: '备注' }
  ],
  其它成本: [
    { key: 'packageFee', label: '包装费' },
    { key: 'transportFee', label: '运输费' }
  ],
  利润: [
    { key: 'profitRate', label: '利润率(%)' }
  ],
  税金: [
    { key: 'taxRate', label: '税率(%)' }
  ]
}

/** 模板 CostEstimateTemplateBody.item_no 归一化后 → 上表 UI 字段 key，用于只读规则（不用于列） */
const TEMPLATE_KEY_TO_UI_KEYS: Record<string, Record<string, string[]>> = {
  材料成本: {
    material: ['material'],
    materialspec: ['material'],
    length: ['len'],
    len: ['len'],
    width: ['width'],
    height: ['height'],
    specificgravity: ['specificgravity'],
    qty: ['qty'],
    weight: ['weight'],
    unitprice: ['unitPrice'],
    unit_price: ['unitPrice'],
    materialcost: ['material_fee'],
    material_cost: ['material_fee'],
    remark: ['remark'],
    partno: ['part_id'],
    part_id: ['part_id']
  },
  加工成本: {
    processstation: ['processStation'],
    process_station: ['processStation'],
    unit: ['processUnit'],
    processunit: ['processUnit'],
    unitrate: ['processRate'],
    unit_rate: ['processRate'],
    rate: ['processRate'],
    processqty: ['processMeasure'],
    process_qty: ['processMeasure'],
    processprice: ['processFee'],
    process_price: ['processFee'],
    remark: ['remark'],
    partno: ['part_id'],
    part_id: ['part_id']
  },
  其它成本: {
    packagingcost: ['packageFee'],
    packaging_cost: ['packageFee'],
    transportationcost: ['transportFee'],
    transportation_cost: ['transportFee'],
    partno: ['part_id'],
    part_id: ['part_id']
  },
  利润: {
    profitrate: ['profitRate'],
    profit_rate: ['profitRate'],
    partno: ['part_id'],
    part_id: ['part_id']
  },
  税金: {
    taxrate: ['taxRate'],
    tax_rate: ['taxRate'],
    partno: ['part_id'],
    part_id: ['part_id']
  }
}

const normTplKey = (k: string) => String(k || '').toLowerCase().replace(/[^a-z0-9]/g, '')

/** 模板未声明某固定列时的列标题兜底（与 merge 补列一致） */
const labelFallbacks: Record<string, string> = {
  material: '材质',
  material_cost: '材料费用',
  material_fee: '材料费用',
  materialFee: '材料费用',
  material_amount: '材料费用',
  materialAmount: '材料费用',
  specificgravity: '比重',
  density: '比重',
  weight: '重量',
  length: '长',
  len: '长',
  width: '宽',
  height: '高',
  qty: '数量',
  quantity: '数量',
  unitPrice: '单价',
  unitprice: '单价',
  price: '单价',
  unit_price: '单价',
  process_station: '加工工站',
  processStation: '加工工站',
  process_unit: '单位',
  unit: '单位',
  unitrate: '费率',
  rate: '费率',
  process_rate: '费率',
  fee_rate: '费率',
  processqty: '加工计量',
  process_qty: '加工计量',
  processprice: '加工费',
  process_cost: '加工费',
  fee: '加工费',
  process_fee: '加工费',
  packageFee: '包装费',
  transportFee: '运输费',
  profitRate: '利润率(%)',
  taxRate: '税率(%)'
}

const templateFieldDisplayLabel = (f: any, rawKey: string) =>
  String(f?.label ?? f?.nameCn ?? f?.name_cn ?? f?.name ?? rawKey).trim() || rawKey

/**
 * 成本结构列：与 miscInquiryDetail 一致，优先按 `template_sections` 各段 `fields` 顺序与中文名展示；
 * 模板字段 key 经 TEMPLATE_KEY_TO_UI_KEYS 映射到报价单 UI 存储键；无模板字段时回退 FIXED_QUOTATION_SECTION_COLUMNS。
 */
const mergeQuotationSectionColumns = (section: string, templateSections: any): QuotationCostColumn[] => {
  const fixedFallback = [...(FIXED_QUOTATION_SECTION_COLUMNS[section] || [])]
  const tpl = normalizeSections(templateSections).find(
    (s: any) => (s.title || s.name || s.section || '') === section
  )
  const fields = Array.isArray(tpl?.fields) ? tpl.fields : []
  const keyMap = TEMPLATE_KEY_TO_UI_KEYS[section] || {}

  if (!fields.length) {
    return fixedFallback
  }

  const out: QuotationCostColumn[] = []
  const seen = new Set<string>()

  for (const f of fields) {
    const rawKey = String(f?.key || '').trim()
    if (!rawKey) continue
    const nk = normTplKey(rawKey)
    if (section === '加工成本' && (nk === 'processfee' || rawKey === 'process_fee')) continue
    if (nk === 'partid' || rawKey === 'part_id') continue

    const uiKeys: string[] = keyMap[nk] || keyMap[String(f.key).toLowerCase()] || []
    const uiKey = uiKeys.length ? uiKeys[0] : rawKey
    if (seen.has(uiKey)) continue
    seen.add(uiKey)
    out.push({ key: uiKey, label: templateFieldDisplayLabel(f, rawKey) })
  }

  for (const fc of fixedFallback) {
    if (!seen.has(fc.key)) {
      seen.add(fc.key)
      out.push({
        key: fc.key,
        label: labelFallbacks[fc.key] || fc.label
      })
    }
  }

  return out.length ? out : fixedFallback
}

const costTemplates: Record<string, CostTemplateItem[]> = {
  default: [
    {
      section: '材料成本',
      span: 'wide',
      allowAdd: true,
      attrs: [
        { key: 'material', label: '材质', value: '' },
        { key: 'len', label: '长', value: '' },
        { key: 'width', label: '宽', value: '' },
        { key: 'height', label: '高', value: '' },
        { key: 'density', label: '比重', value: '' },
        { key: 'qty', label: '数量', value: '' },
        { key: 'weight', label: '重量', value: '' },
        { key: 'unitPrice', label: '单价', value: '' },
        { key: 'materialTotal', label: '材料成本合计', value: '' }
      ]
    },
    {
      section: '加工成本',
      span: 'wide',
      allowAdd: true,
      attrs: [
        { key: 'processStation', label: '加工工站', value: '' },
        { key: 'processUnit', label: '单位', value: '' },
        { key: 'processRate', label: '费率', value: '' },
        { key: 'processMeasure', label: '加工计量', value: '' },
        { key: 'processFee', label: '加工费', value: '' },
        { key: 'processTotal', label: '加工成本合计', value: '' }
      ]
    },
    {
      section: '管销研费用',
      attrs: [
        { key: 'overheadType', label: '费用类别', value: '' },
        { key: 'overheadTotal', label: '费用', value: '' }
      ]
    },
    {
      section: '其他费用',
      attrs: [
        { key: 'packageFee', label: '包装费', value: '' },
        { key: 'transportFee', label: '运输费', value: '' },
        { key: 'otherTotal', label: '合计', value: '' }
      ]
    },
    {
      section: '利润',
      attrs: [
        { key: 'profitRate', label: '利润率(%)', value: '' },
        { key: 'profitTotal', label: '利润金额', value: '' }
      ]
    },
    {
      section: '税金',
      attrs: [
        { key: 'taxRate', label: '税率(%)', value: '' },
        { key: 'taxTotal', label: '税金金额', value: '' }
      ]
    }
  ],
  tooling: [],
  equipment: [],
  plastic: []
}

const resolveTemplate = (key: string) => (costTemplates[key]?.length ? costTemplates[key] : costTemplates.default)

const normalizeSections = (sections: any) => {
  if (!sections) return []
  if (typeof sections === 'string') {
    try {
      const parsed = JSON.parse(sections)
      return Array.isArray(parsed) ? parsed : []
    } catch (e) {
      return []
    }
  }
  return Array.isArray(sections) ? sections : []
}

const allowedSectionsForTemplate = (sections: any, enableCostStructure = true) => {
  const base = enableCostStructure ? costEnabledSections : costDisabledSections
  const tplSections = normalizeSections(sections)
  const templateSections = tplSections
    .filter((s: any) => s?.enabled !== false)
    .map((s: any) => s.title || s.name || s.section || '')
    .filter(Boolean)
  const allowed = templateSections.length ? base.filter((t) => templateSections.includes(t)) : base
  return allowed.length ? allowed : base
}

/** 与 CostEstimateTemplateHead.is_can_add_materials / is_can_add_process 对应；后端 template_sections 每段带 supplierCanAddRow */
const supplierAddRowAllowed = (v: any) => Boolean(v === true || v === 1 || v === '1')

const buildSectionAddConfig = (sections: any, enableCostStructure = true) => {
  const allowed = allowedSectionsForTemplate(sections, enableCostStructure)
  const map: Record<string, boolean> = {}
  const list = normalizeSections(sections)
  list.forEach((s: any) => {
    const title = s.title || s.name || s.section || ''
    if (!title || !allowed.includes(title)) return
    if (title === '材料成本' || title === '加工成本') {
      map[title] = supplierAddRowAllowed(s.supplierCanAddRow)
      return
    }
    if (title === '其它成本') {
      map[title] = false
      return
    }
    map[title] = s.supplierCanAddRow !== false
  })
  if (allowed.includes('其它成本')) {
    map['其它成本'] = false
  }
  // 模板未返回材料/加工段时无 supplierCanAddRow，默认允许增行（兼容旧数据）
  allowed.forEach((title) => {
    if (title === '材料成本' || title === '加工成本') {
      if (map[title] === undefined) map[title] = true
    }
  })
  return map
}

const buildRowsFromTemplate = (sections: any, enableCostStructure = true): CostRow[] => {
  const allowed = allowedSectionsForTemplate(sections, enableCostStructure)
  const rows: CostRow[] = []
  allowed.forEach((title: string, idx: number) => {
    const cols = mergeQuotationSectionColumns(title, sections)
    const values: Record<string, any> = {}
    const labels: Record<string, string> = {}
    ;(cols || []).forEach((c) => {
      values[c.key] = ''
      labels[c.key] = c.label
    })
    rows.push({ id: `tpl-${title}-${idx}-${Date.now()}`, section: title, field: `tpl-${title}-${idx}`, values, labels })
  })
  if (!rows.length) {
    return costDisabledSections.map((title, idx) => ({ id: `def-${idx}-${Date.now()}`, section: title, field: `def-${idx}`, values: {}, labels: {} }))
  }
  return rows
}

const costItemsToRows = (items: CostItem[] = [], sections: any, enableCostStructure = true): CostRow[] => {
  const rows: CostRow[] = []
  const allowed = new Set(allowedSectionsForTemplate(sections, enableCostStructure))
  items.forEach((item, idx) => {
    if (!allowed.has(item.section)) return
    const baseId = item.id || `c-${idx}-${Date.now()}`
    const values: Record<string, any> = {}
    const labels: Record<string, string> = {}
    const attrs = Array.isArray(item.attrs) ? item.attrs : []
    attrs.forEach((a: any) => {
      if (materialTotalKeys.includes(a.key)) return
      if (processTotalKeys.includes(a.key)) return
      values[a.key || ''] = a.value ?? ''
      if (a.key) labels[a.key] = a.label || a.key
    })
    if (item.section === '材料成本' || item.section === '加工成本') {
      mergeQuotationSectionColumns(item.section, sections).forEach((c) => {
        if (!(c.key in values)) {
          values[c.key] = ''
          if (!labels[c.key]) labels[c.key] = c.label
        }
      })
    }
    const partId = (values.part_id || values.partId || '') as string
    rows.push({
      id: `${baseId}-0`,
      section: item.section || '',
      field: item.field || item.id || '',
      values,
      labels,
      partId: partId || undefined
    })
  })
  return rows
}

const rowsToCostItems = (
  rows: CostRow[],
  sectionColumns: Record<string, { key: string; label: string }[]>,
  enabledSections: string[]
): CostItem[] => {
  const allowed = new Set(enabledSections)
  return rows
    .filter((r) => allowed.has(r.section))
    .map((r, idx) => {
      const labelMap = new Map<string, string>((sectionColumns[r.section] || []).map((c) => [c.key, c.label]))
      const attrs = Object.entries(r.values || {})
        .filter(
          ([k]) =>
            !(r.section === '材料成本' && materialTotalKeys.includes(k)) &&
            !(r.section === '加工成本' && processTotalKeys.includes(k))
        )
        .map(([k, v]) => ({
          key: k,
          label: (r.labels && r.labels[k]) || labelMap.get(k) || k,
          value: v ?? ''
        }))
      return { id: r.id || `c-${idx}`, section: r.section, span: undefined, attrs }
    })
}

const buildCostItemsFromTemplateSections = (sections: any, enableCostStructure = true): CostItem[] => {
  const allowed = allowedSectionsForTemplate(sections, enableCostStructure)
  return allowed
    .map((title: string) => {
      const cols = mergeQuotationSectionColumns(title, sections)
      if (!cols?.length) return null
      return {
        id: crypto.randomUUID(),
        section: title,
        span: title === '材料成本' || title === '加工成本' ? 'wide' : undefined,
        attrs: cols.map((c) => ({ key: c.key, label: c.label, value: '' }))
      }
    })
    .filter(Boolean) as CostItem[]
}

const buildDefaultNonBomCostItems = (): CostItem[] => {
  const productDetail: CostItem = {
    id: crypto.randomUUID(),
    section: '产品明细',
    attrs: [
      { key: 'partNo', label: '料号', value: '' },
      { key: 'desc', label: '规格描述', value: '' },
      { key: 'qty', label: '数量', value: '' },
      { key: 'price', label: '单价', value: '' },
      { key: 'amount', label: '合计价格', value: '' }
    ]
  }
  const profit: CostItem = {
    id: crypto.randomUUID(),
    section: '利润',
    attrs: [{ key: 'profitRate', label: '利润率', value: '' }]
  }
  const tax: CostItem = {
    id: crypto.randomUUID(),
    section: '税金',
    attrs: [{ key: 'taxRate', label: '税率', value: '' }]
  }
  return [productDetail, profit, tax]
}

const normalizeCostItems = (value: any): CostItem[] => {
  let parsed = value
  if (typeof value === 'string') {
    try {
      parsed = JSON.parse(value)
    } catch (e) {
      parsed = []
    }
  }
  if (!Array.isArray(parsed)) return []
  return parsed.map((item: any, idx: number) => ({
    id: item.id || `c-${idx}-${Date.now()}`,
    section: item.section || item.name || '未分组',
    span: item.span,
    attrs: Array.isArray(item.attrs)
      ? item.attrs.map((a: any) => ({ key: a.key || '', label: a.label || a.key || '', value: a.value ?? '' }))
      : []
  }))
}

const parseJsonLoose = (s: any): Record<string, any> => {
  if (!s || typeof s !== 'string') return {}
  try {
    const o = JSON.parse(s)
    return o && typeof o === 'object' ? o : {}
  } catch {
    return {}
  }
}

/** 后端 GET 详情为嵌套 material_costs / process_costs 等，与前端 cost_items 无关 */
export const hasQuotationNestedCosts = (item: any): boolean =>
  !!item &&
  ((Array.isArray(item.material_costs) && item.material_costs.length > 0) ||
    (Array.isArray(item.process_costs) && item.process_costs.length > 0) ||
    (Array.isArray(item.other_costs) && item.other_costs.length > 0) ||
    (Array.isArray(item.profit_costs) && item.profit_costs.length > 0))

/** 将详情嵌套子表转为 CostItem[]，供 costItemsToRows 渲染 */
const costItemsFromQuotationApi = (item: any): CostItem[] => {
  const out: CostItem[] = []
  let mid = 0
  for (const m of item.material_costs || []) {
    const opt = parseJsonLoose(m.option_json)
    const attrs: { key: string; label: string; value: any }[] = [
      { key: 'part_id', label: '料号', value: m.part_id ?? '' },
      { key: 'material', label: '材质', value: m.material_spec ?? '' },
      { key: 'len', label: '长', value: m.length ?? '' },
      { key: 'width', label: '宽', value: m.width ?? '' },
      { key: 'height', label: '高', value: m.height ?? '' },
      { key: 'specificgravity', label: '比重', value: m.specific_gravity ?? '' },
      { key: 'qty', label: '数量', value: m.qty ?? '' },
      { key: 'weight', label: '重量', value: m.weight ?? '' },
      { key: 'unitPrice', label: '单价', value: m.unit_price ?? '' },
      { key: 'material_fee', label: '材料费用', value: m.material_cost ?? '' },
      { key: 'remark', label: '备注', value: m.remark ?? '' }
    ]
    Object.entries(opt).forEach(([k, v]) => {
      if (!attrs.find((a) => a.key === k)) attrs.push({ key: k, label: k, value: v })
    })
    out.push({
      id: `mat-${m.autoid ?? mid++}`,
      section: '材料成本',
      span: 'wide',
      attrs
    })
  }
  let pid = 0
  for (const p of item.process_costs || []) {
    const opt = parseJsonLoose(p.option_json)
    const attrs: { key: string; label: string; value: any }[] = [
      { key: 'part_id', label: '料号', value: p.part_id ?? '' },
      { key: 'processStation', label: '加工工站', value: p.process_station ?? '' },
      { key: 'processUnit', label: '单位', value: p.unit ?? '' },
      { key: 'processRate', label: '费率', value: p.unit_rate ?? '' },
      { key: 'processMeasure', label: '加工计量', value: p.process_qty ?? '' },
      { key: 'processFee', label: '加工费', value: p.process_price ?? '' },
      { key: 'remark', label: '备注', value: p.remark ?? '' }
    ]
    Object.entries(opt).forEach(([k, v]) => {
      if (!attrs.find((a) => a.key === k)) attrs.push({ key: k, label: k, value: v })
    })
    out.push({
      id: `proc-${p.autoid ?? pid++}`,
      section: '加工成本',
      span: 'wide',
      attrs
    })
  }
  let oid = 0
  for (const o of item.other_costs || []) {
    out.push({
      id: `oth-${o.autoid ?? oid++}`,
      section: '其它成本',
      attrs: [
        { key: 'part_id', label: '料号', value: o.part_id ?? '' },
        { key: 'packageFee', label: '包装费', value: o.packaging_cost ?? '' },
        { key: 'transportFee', label: '运输费', value: o.transportation_cost ?? '' }
      ]
    })
  }
  for (const pr of item.profit_costs || []) {
    const pid = pr.part_id ?? ''
    out.push({
      id: `profit-${pr.autoid ?? pid}-p`,
      section: '利润',
      attrs: [
        { key: 'part_id', label: '料号', value: pid },
        { key: 'profitRate', label: '利润率(%)', value: pr.profit_rate ?? '' },
        { key: 'profitTotal', label: '利润金额', value: '' }
      ]
    })
    out.push({
      id: `profit-${pr.autoid ?? pid}-t`,
      section: '税金',
      attrs: [
        { key: 'part_id', label: '料号', value: pid },
        { key: 'taxRate', label: '税率(%)', value: pr.tax_rate ?? '' },
        { key: 'taxTotal', label: '税金金额', value: '' }
      ]
    })
  }
  return out
}

const numOrUndef = (v: any) => {
  if (v === '' || v === undefined || v === null) return undefined
  const n = Number(v)
  return Number.isFinite(n) ? n : undefined
}

/** 加工成本等单位字段：文本（与 QuotationProcess.unit CharField 一致） */
const strOrNullSlice = (v: any, maxLen: number) => {
  if (v === '' || v === undefined || v === null) return null
  const s = String(v).trim()
  return s ? s.slice(0, maxLen) : null
}

/** 将当前表格行写回后端 QuotationMasterCreateUpdateSerializer 期望的嵌套字段 */
const costRowsToNestedPayload = (rows: CostRow[]) => {
  const material_costs: any[] = []
  const process_costs: any[] = []
  const other_costs: any[] = []
  const profitByPart = new Map<string, { profit_rate?: number; tax_rate?: number }>()

  const materialKnown = new Set([
    'part_id',
    'material',
    'material_spec',
    'len',
    'length',
    'width',
    'height',
    'specificgravity',
    'qty',
    'unitPrice',
    'unit_price',
    'material_fee',
    'material_cost',
    'remark',
    'weight'
  ])
  const processKnown = new Set([
    'part_id',
    'processStation',
    'process_station',
    'processUnit',
    'unit',
    'processRate',
    'unit_rate',
    'rate',
    'processMeasure',
    'process_qty',
    'processFee',
    'process_price',
    'remark'
  ])

  for (const r of rows) {
    const v = r.values || {}
    const partId = String(r.partId || v.part_id || v.partId || '').trim()
    if (r.section === '材料成本') {
      const extra: Record<string, any> = {}
      Object.entries(v).forEach(([k, val]) => {
        if (!materialKnown.has(k) && val !== '' && val !== undefined && val !== null) extra[k] = val
      })
      material_costs.push({
        part_id: partId,
        material_spec: String(v.material ?? v.material_spec ?? '').slice(0, 20),
        length: v.len != null && v.len !== '' ? String(v.len).slice(0, 10) : v.length != null ? String(v.length).slice(0, 10) : null,
        width: v.width != null && v.width !== '' ? String(v.width).slice(0, 10) : null,
        height: v.height != null && v.height !== '' ? String(v.height).slice(0, 10) : null,
        unit_price: numOrUndef(v.unitPrice ?? v.unit_price),
        qty: numOrUndef(v.qty),
        specific_gravity:
          v.specificgravity != null && v.specificgravity !== ''
            ? String(v.specificgravity).slice(0, 10)
            : v.specific_gravity != null
              ? String(v.specific_gravity).slice(0, 10)
              : null,
        material_cost: numOrUndef(v.material_fee ?? v.material_cost),
        weight: numOrUndef(v.weight),
        remark: v.remark ? String(v.remark).slice(0, 100) : null,
        option_json: Object.keys(extra).length ? JSON.stringify(extra) : null
      })
    } else if (r.section === '加工成本') {
      const extra: Record<string, any> = {}
      Object.entries(v).forEach(([k, val]) => {
        if (!processKnown.has(k) && val !== '' && val !== undefined && val !== null) extra[k] = val
      })
      process_costs.push({
        part_id: partId,
        process_station: v.processStation != null ? String(v.processStation).slice(0, 20) : v.process_station != null ? String(v.process_station).slice(0, 20) : null,
        unit: strOrNullSlice(v.processUnit ?? v.unit, 20),
        unit_rate: numOrUndef(v.processRate ?? v.unit_rate ?? v.rate),
        process_qty: v.processMeasure != null ? String(v.processMeasure) : v.process_qty != null ? String(v.process_qty) : null,
        process_price: numOrUndef(v.processFee ?? v.process_price),
        remark: v.remark ? String(v.remark).slice(0, 100) : null,
        option_json: Object.keys(extra).length ? JSON.stringify(extra) : null
      })
    } else if (r.section === '其它成本') {
      other_costs.push({
        part_id: partId,
        packaging_cost: numOrUndef(v.packageFee),
        transportation_cost: numOrUndef(v.transportFee)
      })
    } else if (r.section === '利润') {
      const cur = profitByPart.get(partId) || {}
      cur.profit_rate = numOrUndef(v.profitRate ?? v.profit_rate)
      profitByPart.set(partId, cur)
    } else if (r.section === '税金') {
      const cur = profitByPart.get(partId) || {}
      cur.tax_rate = numOrUndef(v.taxRate ?? v.tax_rate)
      profitByPart.set(partId, cur)
    }
  }

  const profit_costs = Array.from(profitByPart.entries()).map(([pid, rates]) => ({
    part_id: pid,
    profit_rate: rates.profit_rate,
    tax_rate: rates.tax_rate
  }))

  return { material_costs, process_costs, other_costs, profit_costs }
}

/** 详情接口响应解包（列表弹窗与详情页共用） */
export const unwrapQuotationDetail = (res: any): any => {
  const r = res?.data !== undefined ? res.data : res
  if (r && typeof r === 'object' && r.quotation_no != null) return r
  if (r && typeof r === 'object' && r.data && typeof r.data === 'object' && r.data.quotation_no != null) return r.data
  return r
}

const now = () => new Date().toLocaleString()

const toNum = (v: string) => {
  const n = Number(v)
  return Number.isFinite(n) ? n : 0
}

/** 报价合计用：只取「金额类」字段，避免把长宽厚、数量、单价、比重等一并加总 */
const firstDefinedNumericInValues = (values: Record<string, any> | undefined, keyCandidates: string[]) => {
  const v = values || {}
  for (const k of keyCandidates) {
    const raw = v[k]
    if (raw === undefined || raw === null || raw === '') continue
    return toNum(String(raw))
  }
  return 0
}

const otherCostPackagingKeys = ['packageFee', 'packaging_cost', 'packagingCost', 'packaging_fee', '包装费']
const otherCostTransportKeys = ['transportFee', 'transportation_cost', 'transportationCost', 'transport_fee', '运输费']

const formatMoney = (v: number | string) => {
  if (v === '' || v === null || v === undefined) return '-'
  const n = typeof v === 'string' ? Number(v) : v
  if (!Number.isFinite(n)) return '-'
  return n.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

/** 主表无报价金额字段时，由上阶物料明细含税总价汇总 */
const totalInclTaxFromRfqItems = (rfqItems: unknown): number | '' => {
  if (!Array.isArray(rfqItems) || !rfqItems.length) return ''
  let sum = 0
  let any = false
  for (const r of rfqItems) {
    const raw = (r as any)?.total_price_incl_tax ?? (r as any)?.totalPriceInclTax
    if (raw === null || raw === undefined || raw === '') continue
    const n = Number(raw)
    if (Number.isFinite(n)) {
      sum += n
      any = true
    }
  }
  return any ? sum : ''
}

function blankQuote(): Quote {
  return {
    id: '',
    quoteNo: '',
    inquiryCode: '',
    inquiryTitle: '',
    inquiryCompanyCode: '',
    companyShortName: '',
    inquiryStatus: '',
    inquiryStatusCode: undefined,
    template: '',
    currency: 'CNY',
    buyingMethod: 1,
    bidStartTime: '',
    bidEndTime: '',
    quoteDeadline: '',
    quoteAmount: '',
    quoteTime: '',
    status: 'pending',
    statusCode: 1,
    isAwarded: 0,
    supplierCode: '',
    supplierName: '',
    base: { contact: '', phone: '', email: '', validityDays: '', leadTimeDays: '', paymentTerm: '' },
    costItems: [],
    attachments: [],
    inquiryAttachments: [],
    remark: '',
    createdAt: '',
    templateSections: [],
    enableCostStructure: true,
    rfqItems: []
  }
}

export function useQuoteCrud(options?: {
  onChange?: () => void
  /** 列表页用弹窗；详情页用独立路由，不打开 dialog */
  uiContext?: 'list' | 'detail'
  /** 详情页保存成功后（例如返回列表） */
  onSaveSuccess?: () => void
}) {
  const uiContext = options?.uiContext ?? 'list'
  const filters = reactive<{
    inquiryPlant: string
    isAwarded: string | number | ''
    buyingMethod: string | number | ''
    quoteNo?: string
    inquiryCode?: string
    inquiryTitle?: string
    currency?: string
    dateRange: [Date, Date] | []
  }>({
    inquiryPlant: '',
    isAwarded: '',
    buyingMethod: '',
    quoteNo: '',
    inquiryCode: '',
    inquiryTitle: '',
    currency: '',
    dateRange: []
  })
  const quotes = ref<Quote[]>([])
  const dialog = reactive({ visible: false, mode: 'edit' as 'edit' | 'view', quoteId: '' })
  const current = reactive<Quote>(blankQuote())
  const loading = ref(false)
  const costRows = ref<CostRow[]>([])
  const sectionAddConfig = ref<Record<string, boolean>>({})

  const templateSectionMap = computed(() => {
    const map = new Map<string, any>()
    normalizeSections(current.templateSections).forEach((s: any) => {
      const title = s.title || s.name || s.section || ''
      if (title) map.set(title, s)
    })
    return map
  })

  const enabledSections = computed(() => allowedSectionsForTemplate(current.templateSections, current.enableCostStructure !== false))
  const profitTaxNames = ['利润', '税金']
  const profitTaxSections = computed(() => enabledSections.value.filter((s) => profitTaxNames.includes(s)))
  const primarySections = computed(() => enabledSections.value.filter((s) => !profitTaxNames.includes(s)))

  type CostFieldColumn = QuotationCostColumn & {
    isComputed?: boolean
    supplierRequired?: number
  }

  /** 仅用于只读：询价成本模板字段 → 映射到本页固定 UI 键 */
  const templateUiLockBySection = computed(() => {
    const out = new Map<string, Map<string, { isComputed: boolean; supplierRequired: number }>>()
    enabledSections.value.forEach((section) => {
      const m = new Map<string, { isComputed: boolean; supplierRequired: number }>()
      const tplSec = templateSectionMap.value.get(section)
      const keyMap = TEMPLATE_KEY_TO_UI_KEYS[section] || {}
      ;(tplSec?.fields || []).forEach((f: any) => {
        if (!f?.key) return
        const ic =
          Number(f.is_computed ?? f.isComputed ?? (f.autoFill ? 1 : 0)) === 1 || f.autoFill === true
        const sr = Number(f.supplier_required ?? f.supplierRequired ?? 0)
        const nk = normTplKey(f.key)
        const uiKeys = keyMap[nk] || keyMap[String(f.key).toLowerCase()] || [f.key]
        uiKeys.forEach((uk) => {
          m.set(uk, { isComputed: ic, supplierRequired: sr })
        })
      })
      out.set(section, m)
    })
    return out
  })

  /** 固定列 + 模板定义的扩展列（仅材料/加工，与 option_json 一致）；锁格规则仍来自 template_sections */
  const sectionColumns = computed<Record<string, CostFieldColumn[]>>(() => {
    const res: Record<string, CostFieldColumn[]> = {}
    const tpl = current.templateSections
    enabledSections.value.forEach((section) => {
      const merged = mergeQuotationSectionColumns(section, tpl)
      const locks = templateUiLockBySection.value.get(section) || new Map()
      res[section] = merged.map((col) => {
        const meta = locks.get(col.key)
        return {
          ...col,
          isComputed: meta?.isComputed ?? false,
          supplierRequired: meta?.supplierRequired ?? 0
        }
      })
    })
    return res
  })

  /** 模板：is_computed=1 或 supplier_required=1（带出不可改）时供应商不可编辑 */
  const isSupplierFieldLocked = (section: string, colKey: string) => {
    const cols = sectionColumns.value[section] || []
    const col = cols.find((c) => c.key === colKey)
    if (!col) return false
    return col.isComputed === true || Number(col.supplierRequired) === 1
  }

  const isCostCellDisabled = (section: string, colKey: string) => {
    if (dialog.mode === 'view') return true
    return isSupplierFieldLocked(section, colKey)
  }

  const groupedCostRows = computed<Record<string, CostRow[]>>(() => {
    const map: Record<string, CostRow[]> = {}
    enabledSections.value.forEach((s) => {
      map[s] = []
    })
    costRows.value.forEach((r) => {
      const sec = r.section || '未分组'
      if (!enabledSections.value.includes(sec)) return
      if (!map[sec]) map[sec] = []
      map[sec].push(r)
    })
    if (map['其它成本']) {
      if (!map['其它成本'].length) {
        const cols = sectionColumns.value['其它成本'] || []
        const values: Record<string, any> = {}
        const labels: Record<string, string> = {}
        cols.forEach((c) => {
          values[c.key] = ''
          labels[c.key] = c.label
        })
        map['其它成本'] = [{ id: 'other-default', section: '其它成本', field: 'other-default', values, labels }]
      } else if (map['其它成本'].length > 1) {
        map['其它成本'] = [map['其它成本'][0]]
      }
    }
    return map
  })

  const normalizeStatus = (s: any): QuoteStatus => {
    if (s === null || s === undefined || s === '') return 'pending'
    if (typeof s === 'number') return statusMapBackendToFront[s] || 'pending'

    // 兼容后端返回 "1" / "2" 这种字符串数字
    const str = String(s).trim()
    if (/^\d+$/.test(str)) return statusMapBackendToFront[Number(str)] || 'pending'

    // 已是前端枚举值
    if (str === 'pending' || str === 'quoted' || str === 'completed' || str === 'expired') return str as QuoteStatus

    // 兼容后端/历史数据直接返回中文文案的情况
    const labelToStatus: Record<string, QuoteStatus> = {
      待报价: 'pending',
      报价中: 'quoted',
      已报价: 'completed',
      已过期: 'expired'
    }
    return labelToStatus[str] || 'pending'
  }

  const normalizePayment = (p: any) => {
    if (typeof p === 'number') return paymentMapBackendToFront[p] || ''
    return p || ''
  }

  const costItemsForCurrent = computed(() => rowsToCostItems(costRows.value, sectionColumns.value, enabledSections.value))

  const applySectionAddConfig = (sections: any) => {
    sectionAddConfig.value = buildSectionAddConfig(sections, current.enableCostStructure !== false)
  }

  const loadCostRowsFromTemplate = (sections: any, force = false) => {
    const rows = buildRowsFromTemplate(sections, current.enableCostStructure !== false)
    if (force || !costRows.value.length) {
      costRows.value = rows
    }
    applySectionAddConfig(sections)
  }

  applySectionAddConfig([])

  const materialOptions = ref<{ value: string; label: string; density?: number; price?: number }[]>([])
  const materialLoading = ref(false)
  const stationOptions = ref<{ value: string; label: string; rate?: number; unit?: string }[]>([])
  const stationLoading = ref(false)
  const unitOptions = ref<{ value: string; label: string }[]>([])
  const unitLoading = ref(false)
  /** 杂采料号 MiscProcMaterial：partid → 物料说明、单位，回填 rfq_items */
  const miscPartByPartId = ref<Record<string, { partid_name: string; unit: string }>>({})

  /** `CostEstimateTemplateHead.template_no` -> 模板名称 */
  const templateNameByCode = ref<Record<string, string>>({})
  let templateNameLookupDone = false

  const ensureTemplateNameLookup = async () => {
    if (templateNameLookupDone) return
    templateNameLookupDone = true
    try {
      const costRes = await GetCostTemplateList({ page: 1, page_size: 500, pageSize: 500 } as any)
      const merge: Record<string, string> = {}
      for (const row of extractPagedList(costRes)) {
        const no = row.template_no
        if (no) merge[String(no).trim()] = trim(row.template_name) || String(no)
      }
      templateNameByCode.value = merge
    } catch (e) {
      console.warn('加载询价模板名称失败', e)
    }
  }

  function trim(s: unknown) {
    return s == null ? '' : String(s).trim()
  }

  /** 报价主表无询价名称/模板编号，按 `inquiry_no` 拉取询价主表补全（与 `Inquiry.title` / `Inquiry.template` 一致） */
  const enrichQuotesWithInquiryData = async (items: Quote[]) => {
    const codes = [...new Set(items.map((q) => q.inquiryCode).filter(Boolean))]
    if (!codes.length) return
    const pairs = await Promise.all(
      codes.map(async (code) => {
        try {
          const res = await inquiryApi.GetList({
            inquiry_no: code,
            page: 1,
            page_size: 1,
            pageSize: 1
          })
          const list = extractPagedList(res)
          const row = list[0]
          return row ? { code, row } : null
        } catch {
          return null
        }
      })
    )
    const byCode = new Map<string, any>()
    for (const p of pairs) {
      if (p) byCode.set(p.code, p.row)
    }
    for (const q of items) {
      const inv = byCode.get(q.inquiryCode)
      if (!inv) continue
      q.inquiryTitle = inv.title || q.inquiryTitle
      const tpl = inv.template || inv.template_code
      if (tpl) q.template = tpl
      if (inv.currency) q.currency = inv.currency
      if (inv.quote_deadline != null && String(inv.quote_deadline).trim() !== '') {
        q.quoteDeadline = normalizeQuoteDeadlineFromApi(inv.quote_deadline)
      }
      if (q.buyingMethod == null && inv.buying_method != null && inv.buying_method !== '') {
        const n = Number(inv.buying_method)
        if (Number.isFinite(n)) q.buyingMethod = n
      }
      if (Number(q.buyingMethod) !== 1) {
        if (!q.bidStartTime && inv.bid_start_time) q.bidStartTime = String(inv.bid_start_time).trim()
        if (!q.bidEndTime && inv.bid_end_time) q.bidEndTime = String(inv.bid_end_time).trim()
      }
      const cc = inv.company_code != null && inv.company_code !== '' ? String(inv.company_code).trim() : ''
      if (cc) q.inquiryCompanyCode = cc
      const invSt = inv.status ?? inv.inquiry_status
      if (invSt !== undefined && invSt !== null && invSt !== '') {
        q.inquiryStatusCode = Number(invSt)
      }
      q.inquiryStatus = formatMiscInquiryStatus(q)
    }
  }

  const mapBackendQuote = (item: any): Quote => {
    const quote: Quote = {
      id: String(item.id ?? item.autoid ?? item.quotation_no ?? crypto.randomUUID()),
      quoteNo: item.quotation_no || item.quoteNo || '',
      inquiryCode: item.inquiry_no || item.inquiryCode || '',
      inquiryTitle:
        item.inquiry_name || item.inquiry_title || item.title || item.inquiryTitle || '',
      inquiryCompanyCode:
        item.inquiry_company_code != null && item.inquiry_company_code !== ''
          ? String(item.inquiry_company_code).trim()
          : '',
      companyShortName:
        item.inquiry_company_short_name != null && item.inquiry_company_short_name !== ''
          ? String(item.inquiry_company_short_name).trim()
          : '',
      inquiryStatus: item.inquiry_status || item.inquiryStatus || '',
      inquiryStatusCode:
        item.inquiry_status_code != null && item.inquiry_status_code !== ''
          ? Number(item.inquiry_status_code)
          : item.inquiry?.status != null && item.inquiry?.status !== ''
            ? Number(item.inquiry.status)
            : undefined,
      /** 询价主表 `Inquiry.template` 存模板编号，与报价主表无该字段时需关联询价补全 */
      template: item.template || item.template_code || '',
      currency: item.currency || 'CNY',
      buyingMethod: (() => {
        const raw = item.buying_method ?? item.buyingMethod
        if (raw === null || raw === undefined || raw === '') return null
        const n = Number(raw)
        return Number.isFinite(n) ? n : null
      })(),
      bidStartTime: (() => {
        const raw = item.bid_start_time ?? item.bidStartTime
        return raw != null && String(raw).trim() !== '' ? String(raw).trim() : ''
      })(),
      bidEndTime: (() => {
        const raw = item.bid_end_time ?? item.bidEndTime
        return raw != null && String(raw).trim() !== '' ? String(raw).trim() : ''
      })(),
      quoteDeadline: normalizeQuoteDeadlineFromApi(item.quote_deadline ?? item.quoteDeadline ?? ''),
      quoteAmount:
        item.quote_amount ??
        item.quoteAmount ??
        totalInclTaxFromRfqItems(item.rfq_items) ??
        '',
      quoteTime: item.quotetime || item.quoteTime || '',
      status: normalizeStatus(item.status),
      statusCode: (() => {
        const n = Number(item.status)
        return Number.isFinite(n) ? n : 1
      })(),
      isAwarded: (() => {
        const n = Number(item.is_awarded)
        return Number.isFinite(n) ? n : 0
      })(),
      supplierCode: item.supplier_code || item.supplierCode || '',
      supplierName: item.supplier_name || item.supplierName || '',
      base: {
        contact: item.contact_person || item.contact || '',
        phone: item.contact_phone || item.phone || '',
        email: item.contact_email || item.email || '',
        validityDays: item.validity_days ?? item.validityDays ?? '',
        leadTimeDays: item.delivery_days ?? item.leadTimeDays ?? '',
        paymentTerm: normalizePayment(item.payment_method)
      },
      costItems: hasQuotationNestedCosts(item)
        ? costItemsFromQuotationApi(item)
        : normalizeCostItems(item.cost_items || item.costItems).length
          ? normalizeCostItems(item.cost_items || item.costItems)
          : buildCostItems(
              item.template || item.template_code || 'default',
              item.templateSections || item.template_sections || item.sections,
              (item.enable_cost_structure ?? item.is_bom ?? item.isBom ?? item.template?.enable_cost_structure) !== false
            ),
      rfqItems: Array.isArray(item.rfq_items) ? item.rfq_items : [],
      attachments: normalizeQuotationAttachmentsForUpload(item.attachments),
      inquiryAttachments: Array.isArray(item.inquiry_attachments)
        ? item.inquiry_attachments
        : Array.isArray(item.inquiryAttachments)
          ? item.inquiryAttachments
          : [],
      remark: item.remark || '',
      createdAt: item.creattime || item.creat_time || item.create_time || item.createTime || item.createdAt || '',
      templateSections:
        item.template_sections ||
        item.templateSections ||
        item.sections ||
        item.template?.sections ||
        [],
      enableCostStructure:
        item.enable_cost_structure ?? item.enableCostStructure ?? item.is_bom ?? item.isBom ?? item.template?.enable_cost_structure ?? true
    }
    quote.inquiryStatus = formatMiscInquiryStatus(quote)
    return quote
  }

  const loadMaterialOptions = async () => {
    materialLoading.value = true
    try {
      const res = await GetMaterials({ page: 1, page_size: 300, pageSize: 300 })
      const list = res?.data?.data?.results || res?.data?.results || res?.data?.list || res?.data || res?.results || res?.list || []
      materialOptions.value = (Array.isArray(list) ? list : []).map((m: any) => ({
        value: m.materialtype || m.material || m.name,
        label: m.materialtype || m.material || m.name,
        density: m.density || m.specificgravity,
        price: m.price
      }))
    } catch (e) {
      console.warn('加载材质信息失败', e)
      materialOptions.value = []
    } finally {
      materialLoading.value = false
    }
  }

  const loadStationOptions = async () => {
    stationLoading.value = true
    try {
      const res = await GetStations({ page: 1, page_size: 500, pageSize: 500 })
      const list = res?.data?.data?.results || res?.data?.results || res?.data?.list || res?.data || res?.results || res?.list || []
      stationOptions.value = (Array.isArray(list) ? list : []).map((s: any) => ({
        value: s.stationcode || s.station_code || s.stationname || s.name,
        label: `${s.stationname || s.name || s.stationcode || ''}${s.stationcode ? `（${s.stationcode}）` : ''}`,
        rate: s.rate,
        unit: s.unit || s.process_unit || s.uom || s.station_unit
      }))
    } catch (e) {
      console.warn('加载加工工站失败', e)
      stationOptions.value = []
    } finally {
      stationLoading.value = false
    }
  }

  const loadUnitOptions = async () => {
    unitLoading.value = true
    try {
      const res = await GetUnits({ page: 1, page_size: 500, pageSize: 500 })
      const list = res?.data?.data?.results || res?.data?.results || res?.data?.list || res?.data || res?.results || res?.list || []
      unitOptions.value = (Array.isArray(list) ? list : []).map((u: any) => ({
        value: u.unitcode || u.unit_code || u.unit || u.name,
        label: u.unitname || u.name || u.unitcode || u.unit || '单位'
      }))
    } catch (e) {
      console.warn('加载单位失败', e)
      unitOptions.value = []
    } finally {
      unitLoading.value = false
    }
  }

  const loadMiscPartLookup = async () => {
    try {
      const res = await GetMiscParts({ page: 1, page_size: 2000, pageSize: 2000 })
      const list =
        res?.data?.data?.results || res?.data?.results || res?.data?.list || res?.data || res?.results || res?.list || []
      const map: Record<string, { partid_name: string; unit: string }> = {}
      for (const row of Array.isArray(list) ? list : []) {
        const id = String(row.partid ?? row.part_id ?? '').trim()
        if (!id) continue
        map[id] = {
          partid_name: String(row.partid_name ?? row.partidName ?? ''),
          unit: String(row.unit ?? '')
        }
      }
      miscPartByPartId.value = map
    } catch (e) {
      console.warn('加载杂采料号信息失败', e)
      miscPartByPartId.value = {}
    }
  }

  const loadQuotes = async () => {
    loading.value = true
    try {
      await ensureTemplateNameLookup()
      try {
        await api.syncExpiredQuotations()
      } catch (e) {
        console.warn('同步已过期报价单状态失败', e)
      }
      /** 与后端 dvadmin CustomPagination 一致：每页条数参数为 `limit`（非 page_size），默认 10 会导致列表只拉取 10 条 */
      const res: any = await api.getList({ page: 1, limit: 999 })
      const list = Array.isArray(res?.data)
        ? res.data
        : res?.data?.results || res?.data?.list || res?.results || res?.list || []
      const mapped = (Array.isArray(list) ? list : []).map(mapBackendQuote)
      await enrichQuotesWithInquiryData(mapped)
      quotes.value = mapped
    } catch (e) {
      console.warn('加载报价单失败', e)
    } finally {
      loading.value = false
    }
  }

  onMounted(() => {
    if (uiContext === 'list') {
      loadQuotes()
    }
    loadMaterialOptions()
    loadStationOptions()
    loadUnitOptions()
    loadMiscPartLookup()
  })

  const resetFilter = () => {
    filters.inquiryPlant = ''
    filters.isAwarded = ''
    filters.buyingMethod = ''
    filters.quoteNo = ''
    filters.inquiryCode = ''
    filters.inquiryTitle = ''
    filters.currency = ''
    filters.dateRange = []
  }

  const filteredQuotes = computed(() => {
    const [start, end] = filters.dateRange as [Date | undefined, Date | undefined]
    return quotes.value.filter((q) => {
        const matchQuoteNo = !filters.quoteNo || q.quoteNo.toLowerCase().includes(filters.quoteNo.trim().toLowerCase())
        const matchInquiryCode = !filters.inquiryCode || q.inquiryCode.toLowerCase().includes(filters.inquiryCode.trim().toLowerCase())
        const matchInquiryTitle = !filters.inquiryTitle || q.inquiryTitle.toLowerCase().includes(filters.inquiryTitle.trim().toLowerCase())
        const matchCurrency = !filters.currency || q.currency.toLowerCase().includes(filters.currency.trim().toLowerCase())
        const plantQ = (filters.inquiryPlant || '').trim().toLowerCase()
        const matchPlant =
          !plantQ ||
          (q.companyShortName || '').toLowerCase().includes(plantQ) ||
          (q.inquiryCompanyCode || '').toLowerCase().includes(plantQ)
        const matchAwarded =
          filters.isAwarded === '' || filters.isAwarded === undefined || filters.isAwarded === null
            ? true
            : Number(q.isAwarded) === Number(filters.isAwarded)
        const matchBuying =
          filters.buyingMethod === '' || filters.buyingMethod === undefined || filters.buyingMethod === null
            ? true
            : Number(q.buyingMethod) === Number(filters.buyingMethod)
        const matchDate =
          !start ||
          !end ||
          (() => {
            const t = parseQuoteDeadlineToMs(q.quoteDeadline)
            return !Number.isNaN(t) && t >= start.getTime() && t <= end.getTime()
          })()
        return (
          matchQuoteNo &&
          matchInquiryCode &&
          matchInquiryTitle &&
          matchCurrency &&
          matchPlant &&
          matchAwarded &&
          matchBuying &&
          matchDate
        )
      })
  })

  const costSubtotalSectionNames = ['材料成本', '加工成本', '其它成本', '其他成本'] as const
  const isOtherCostSection = (s: string) => s === '其它成本' || s === '其他成本'

  /** 成本结构「利润率(%)」「税率(%)」按百分数填写（如 13 表示 13%），用于报价合计：金额 = 成本合计 × 率 / 100 */
  const profitSummaryPercentKeys = ['profitRate', 'profit_rate', 'profitrate']
  const taxSummaryPercentKeys = ['taxRate', 'tax_rate', 'taxrate']

  const readFirstPercentFromSection = (section: string, keyCandidates: string[]) => {
    const rows = groupedCostRows.value[section] || []
    for (const row of rows) {
      const v = row.values || {}
      for (const k of keyCandidates) {
        const raw = v[k]
        if (raw === undefined || raw === null || raw === '') continue
        return toNum(String(raw))
      }
    }
    return 0
  }

  const sectionAmountMap = computed(() => {
    const map: Record<string, number> = {}
    const sections = enabledSections.value
    for (const section of sections) {
      if (section === '利润' || section === '税金') continue
      const rows = groupedCostRows.value[section] || []
      if (section === '材料成本') {
        map[section] = rows.reduce(
          (sum, row) => sum + firstDefinedNumericInValues(row.values, materialFeeKeys),
          0
        )
      } else if (section === '加工成本') {
        map[section] = rows.reduce(
          (sum, row) => sum + firstDefinedNumericInValues(row.values, processFeeKeys),
          0
        )
      } else if (section === '其它成本' || section === '其他成本') {
        map[section] = rows.reduce((sum, row) => {
          const v = row.values || {}
          return (
            sum +
            firstDefinedNumericInValues(v, otherCostPackagingKeys) +
            firstDefinedNumericInValues(v, otherCostTransportKeys)
          )
        }, 0)
      } else {
        map[section] = rows.reduce((sum, row) => {
          const values = Object.values(row.values || {})
          const rowSum = values.reduce((acc, val) => acc + toNum(String(val)), 0)
          return sum + rowSum
        }, 0)
      }
    }
    const costSum = costSubtotalSectionNames.filter((s) => sections.includes(s)).reduce((sum, s) => sum + (map[s] ?? 0), 0)
    if (sections.includes('利润')) {
      const rate = readFirstPercentFromSection('利润', profitSummaryPercentKeys)
      map['利润'] = Number(((costSum * rate) / 100).toFixed(4))
    }
    if (sections.includes('税金')) {
      const rate = readFirstPercentFromSection('税金', taxSummaryPercentKeys)
      map['税金'] = Number(((costSum * rate) / 100).toFixed(4))
    }
    return map
  })

  /**
   * 与报价合计表一致，用于写入 QuotationItem（上阶物料明细）汇总字段。
   * 字段语义与 InquiryRfqItem / 后端模型一致：profit_rate、tax_rate 存金额非百分数。
   */
  const quoteRollupForRfq = computed(() => {
    const sections = enabledSections.value
    const map = sectionAmountMap.value
    const amt = (s: string) => map[s] ?? 0
    const material = amt('材料成本')
    const processing = amt('加工成本')
    const other = amt('其它成本') + amt('其他成本')
    const opex = amt('管销研费用')
    const costSum = costSubtotalSectionNames.filter((s) => sections.includes(s)).reduce((sum, s) => sum + amt(String(s)), 0)
    const profitAmt = sections.includes('利润') ? amt('利润') : 0
    const taxAmt = sections.includes('税金') ? amt('税金') : 0
    const preTax = costSum + profitAmt
    const postTax = preTax + taxAmt
    return { material, processing, other, opex, costSum, profitAmt, taxAmt, preTax, postTax }
  })

  const quoteSummaryRows = computed<SummaryRow[]>(() => {
    const sections = enabledSections.value
    const amt = (s: string) => sectionAmountMap.value[s] ?? 0
    const { costSum, profitAmt, taxAmt, preTax, postTax } = quoteRollupForRfq.value

    const rows: SummaryRow[] = []
    let addedCostTotal = false
    let addedPreTax = false

    for (const section of sections) {
      rows.push({ section, amount: amt(section) })

      if (isOtherCostSection(section) && !addedCostTotal) {
        rows.push({ section: '成本合计', amount: costSum, isSubtotal: true })
        addedCostTotal = true
      } else if (section === '利润') {
        if (!addedCostTotal) {
          rows.push({ section: '成本合计', amount: costSum, isSubtotal: true })
          addedCostTotal = true
        }
        rows.push({ section: '税前合计', amount: preTax, isSubtotal: true })
        addedPreTax = true
      } else if (section === '税金') {
        if (!addedCostTotal) {
          rows.push({ section: '成本合计', amount: costSum, isSubtotal: true })
          addedCostTotal = true
        }
        if (!addedPreTax) {
          rows.push({ section: '税前合计', amount: preTax, isSubtotal: true })
          addedPreTax = true
        }
        rows.push({ section: '税后总计', amount: postTax, isSubtotal: true })
      }
    }

    return rows
  })

  /** 与表格「税前合计」一致：成本合计 + 利润（未税） */
  const quoteAmountPreTax = computed(() => quoteRollupForRfq.value.preTax)

  /** 各启用成本段 map 金额之和（一般等于 postTax；保留供兼容） */
  const quoteTotal = computed(() =>
    enabledSections.value.reduce((sum, section) => sum + (sectionAmountMap.value[section] ?? 0), 0)
  )

  /** 询价启用的成本段在 costRows 中无行时补一行空白行，避免仅表格下挂 el-empty；数据在 costRows 内才可保存。 */
  const ensurePlaceholderCostRows = (sections: any, enableCostStructure: boolean) => {
    const allowed = allowedSectionsForTemplate(sections, enableCostStructure)
    const countSection = (sec: string) => costRows.value.filter((r) => r.section === sec).length
    allowed.forEach((sec) => {
      if (countSection(sec) > 0) return
      const cols = mergeQuotationSectionColumns(sec, sections)
      if (!cols?.length) return
      const values: Record<string, any> = {}
      const labels: Record<string, string> = {}
      cols.forEach((c) => {
        values[c.key] = ''
        labels[c.key] = c.label
      })
      costRows.value.push({
        id: `${sec}-ph-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
        section: sec,
        field: `${sec}-ph`,
        values,
        labels
      })
    })
  }

  const fillCurrent = (quote: Quote, rowsFromSource?: CostRow[]) => {
    Object.assign(current, JSON.parse(JSON.stringify(quote)))
    applySectionAddConfig(current.templateSections)
    if (rowsFromSource && rowsFromSource.length) {
      costRows.value = rowsFromSource
    } else {
      const rows = costItemsToRows(current.costItems, current.templateSections, current.enableCostStructure !== false)
      if (rows.length) {
        costRows.value = rows
      } else {
        loadCostRowsFromTemplate(current.templateSections, true)
      }
    }
    ensurePlaceholderCostRows(current.templateSections, current.enableCostStructure !== false)
    current.costItems = costItemsForCurrent.value
  }

  /** 编辑报价：由列表「报价」进入（`?mode=edit`）或本页显式打开；路由无 `mode` 时详情页走 `viewQuote` */
  const openQuote = async (row: Quote) => {
    try {
      await api.syncExpiredQuotations()
    } catch (e) {
      console.warn('同步已过期报价单状态失败', e)
    }
    /** 路由详情仅带 id 时先拉主表，保证招标投标窗口校验正确 */
    let rowForFlow = row
    if (row.id && row.buyingMethod == null) {
      try {
        const preRes = await api.getDetail(row.id)
        const preRaw = unwrapQuotationDetail(preRes)
        if (preRaw) {
          rowForFlow = mapBackendQuote(preRaw)
          await enrichQuotesWithInquiryData([rowForFlow])
        }
      } catch (e) {
        console.warn('预加载报价详情失败', e)
      }
    }
    const bidReason = getSupplierBidWindowRejectReason(rowForFlow)
    if (bidReason) {
      ElMessage.warning(bidReason)
      return
    }
    dialog.mode = 'edit'
    dialog.quoteId = rowForFlow.id
    loading.value = true
    try {
      await ensureTemplateNameLookup()
      let quoteData: Quote = { ...rowForFlow }
      let rawDetail: any = null
      if (rowForFlow.id) {
        // 点击「报价」后先进入报价中(2)，以便后续保存/编辑仍可通过后端校验
        if (isPendingQuotation(rowForFlow)) {
          await api.quoteOfficial(rowForFlow.id)
        }
        try {
          const detailRes = await api.getDetail(rowForFlow.id)
          rawDetail = unwrapQuotationDetail(detailRes)
          if (rawDetail) quoteData = mapBackendQuote(rawDetail)
        } catch (e) {
          console.warn('加载报价详情失败', e)
        }
      }
      // 详情接口若未展开 supplier 字段，保留列表行上的供应商代码/名称（PUT 保存必填）
      if (!quoteData.supplierCode && rowForFlow.supplierCode) quoteData.supplierCode = rowForFlow.supplierCode
      if (!quoteData.supplierName && rowForFlow.supplierName) quoteData.supplierName = rowForFlow.supplierName
      if (quoteData.inquiryStatusCode == null && rowForFlow.inquiryStatusCode != null) {
        quoteData.inquiryStatusCode = rowForFlow.inquiryStatusCode
      }

      let effectiveRows: CostRow[] = []
      let inquirySections: any = quoteData.templateSections
      let inquiry: any = null

      try {
        const inquiryCode = quoteData.inquiryCode || (rowForFlow as any).inquiry_no
        if (inquiryCode) {
          const res = await inquiryApi.GetList({
            inquiry_no: inquiryCode,
            page: 1,
            page_size: 1,
            pageSize: 1
          })
          const list = extractPagedList(res)
          inquiry = list[0]
          if (inquiry) {
            quoteData.inquiryCode = inquiry.inquiry_no || inquiry.code || quoteData.inquiryCode
            quoteData.inquiryTitle = inquiry.title || quoteData.inquiryTitle
            quoteData.template = inquiry.template || inquiry.template_code || quoteData.template
            quoteData.currency = inquiry.currency || quoteData.currency
            if (inquiry.quote_deadline != null && String(inquiry.quote_deadline).trim() !== '') {
              quoteData.quoteDeadline = normalizeQuoteDeadlineFromApi(inquiry.quote_deadline)
            }
            const icc = inquiry.company_code != null && inquiry.company_code !== '' ? String(inquiry.company_code).trim() : ''
            if (icc) quoteData.inquiryCompanyCode = icc
            quoteData.inquiryStatus = inquiry.status || inquiry.inquiry_status || quoteData.inquiryStatus
            // const inqSt = inquiry.status ?? inquiry.inquiry_status
            // if (inqSt !== undefined && inqSt !== null && inqSt !== '') {
            //   quoteData.inquiryStatusCode = Number(inqSt)
            // }
            quoteData.inquiryStatusCode = 2
            inquirySections = inquiry.sections || inquiry.template_sections || inquiry.template?.sections || quoteData.templateSections
            if (Array.isArray(inquirySections) && inquirySections.length) {
              quoteData.templateSections = inquirySections
            }
            quoteData.base.leadTimeDays = inquiry.lead_time_days || inquiry.delivery_days || quoteData.base.leadTimeDays
            quoteData.base.paymentTerm = normalizePayment(inquiry.payment_method ?? inquiry.payment_term)

            const enableCostStructure =
              (inquiry.enable_cost_structure ?? inquiry.is_bom ?? inquiry.isBom ?? quoteData.enableCostStructure) !== false
            quoteData.enableCostStructure = enableCostStructure

            if (rawDetail && hasQuotationNestedCosts(rawDetail)) {
              /** 已落库的报价明细优先，列定义仍用询价模板 sections */
              effectiveRows = costItemsToRows(
                quoteData.costItems,
                inquirySections || quoteData.templateSections,
                quoteData.enableCostStructure !== false
              )
            } else {
              const inquiryCostItems = normalizeCostItems(inquiry.cost_items || inquiry.costItems)
              const inquiryRows = inquiryCostItems.length
                ? costItemsToRows(inquiryCostItems, inquirySections, enableCostStructure)
                : buildRowsFromTemplate(inquirySections, enableCostStructure)

              const quoteRows = costItemsToRows(quoteData.costItems, inquirySections, enableCostStructure)
              effectiveRows = inquiryRows.length ? inquiryRows : quoteRows
            }
          }
        }
      } catch (e) {
        console.warn('加载询价单失败', e)
      }

      if (rawDetail && hasQuotationNestedCosts(rawDetail) && !effectiveRows.length) {
        effectiveRows = costItemsToRows(
          quoteData.costItems,
          inquirySections || quoteData.templateSections,
          quoteData.enableCostStructure !== false
        )
      }
      if (!effectiveRows.length) {
        effectiveRows = costItemsToRows(
          quoteData.costItems,
          quoteData.templateSections,
          quoteData.enableCostStructure !== false
        )
      }

      if (rawDetail?.template_sections?.length) {
        quoteData.templateSections = rawDetail.template_sections
      }

      // 询价附件必须以询价单子表为准（`Inquiry.attachments`），勿用报价单 `attachments` 回显
      if (inquiry?.attachments?.length) {
        quoteData.inquiryAttachments = mapInquiryAttachmentsFromInquiryApi(inquiry.attachments)
      } else if (rawDetail?.inquiry_attachments?.length) {
        quoteData.inquiryAttachments = mapInquiryAttachmentsFromInquiryApi(rawDetail.inquiry_attachments)
      }

      quoteData.inquiryStatus = formatMiscInquiryStatus(quoteData)
      fillCurrent(quoteData, effectiveRows)

      // 让列表行立即反映「报价(2)」状态，保证表格里的「提交」按钮可用
      if (quoteData?.id) {
        const idx = quotes.value.findIndex((q) => q.id === quoteData.id)
        if (idx >= 0) quotes.value.splice(idx, 1, quoteData)
      }
      if (uiContext === 'list') {
        dialog.visible = true
      }
    } finally {
      loading.value = false
    }
  }

  const viewQuote = (row: Quote) => {
    dialog.mode = 'view'
    dialog.quoteId = row.id
    if (uiContext === 'list') {
      dialog.visible = true
    }
    loading.value = true
    ;(async () => {
      try {
        try {
          await api.syncExpiredQuotations()
        } catch (e) {
          console.warn('同步已过期报价单状态失败', e)
        }
        await ensureTemplateNameLookup()
        let merged: Quote = { ...row }
        if (row.id) {
          const detailRes = await api.getDetail(row.id)
          const data = unwrapQuotationDetail(detailRes)
          if (data) merged = mapBackendQuote(data)
        }
        await enrichQuotesWithInquiryData([merged])
        if (!merged.supplierCode && row.supplierCode) merged.supplierCode = row.supplierCode
        if (!merged.supplierName && row.supplierName) merged.supplierName = row.supplierName
        try {
          const code = (merged.inquiryCode || '').trim()
          if (code) {
            const res = await inquiryApi.GetList({
              inquiry_no: code,
              page: 1,
              page_size: 1,
              pageSize: 1
            })
            const list = extractPagedList(res)
            const inv = list[0]
            if (inv?.attachments?.length) {
              merged.inquiryAttachments = mapInquiryAttachmentsFromInquiryApi(inv.attachments)
            }
          }
        } catch (e) {
          console.warn('加载询价附件失败', e)
        }
        fillCurrent(merged)
      } catch (e) {
        console.warn('加载报价详情失败', e)
        fillCurrent(row)
      } finally {
        loading.value = false
      }
    })()
  }

  const toNumber = (v: any) => {
    const n = Number(v)
    return Number.isFinite(n) ? n : 0
  }

  const pickSectionKey = (
    section: string,
    values: Record<string, any>,
    candidates: string[],
    labelCandidates: string[]
  ) => {
    for (const key of candidates) {
      if (Object.prototype.hasOwnProperty.call(values, key)) return key
    }
    const cols = sectionColumns.value[section] || []
    const byKey = cols.find((c) => candidates.includes(c.key))
    if (byKey) return byKey.key
    const byLabel = cols.find((c) => labelCandidates.includes(c.label))
    if (byLabel) return byLabel.key
    return candidates[0]
  }

  const pickKey = (values: Record<string, any>, candidates: string[], fallback: string) => {
    for (const key of candidates) {
      if (values[key] !== undefined) return key
    }
    return fallback
  }

  const updateMaterialCalc = (row: CostRow) => {
    if (!row || row.section !== '材料成本') return
    if (!row.values) row.values = {}
    const v = row.values
    const sgKey = pickKey(v, specificGravityKeys, 'specificgravity')
    const lengthKey = pickKey(v, lengthKeys, 'length')
    const widthKey = pickKey(v, widthKeysForCalc, 'width')
    const heightKey = pickKey(v, heightKeys, 'height')
    const qtyKey = pickKey(v, quantityKeys, 'qty')
    const length = toNumber(v[lengthKey])
    const width = toNumber(v[widthKey])
    const height = toNumber(v[heightKey])
    const sg = toNumber(v[sgKey])
    const qty = toNumber(v[qtyKey])
    const unitPrice = toNumber(v.unitPrice ?? v.unitprice ?? v.price ?? v.unit_price)
    const weightKey = pickKey(v, weightKeys, 'weight')
    const feeKey = pickKey(v, materialFeeKeys, 'material_cost')
    const weight = length * width * height * sg * qty
    v[weightKey] = Number(weight.toFixed(4))
    const materialFee = toNumber(v[weightKey]) * unitPrice
    v[feeKey] = Number(materialFee.toFixed(4))
  }

  const handleMaterialSelect = (row: CostRow, value?: string) => {
    if (!row || !row.values) return
    row.values.material = value || ''
    const material = materialOptions.value.find((m) => m.value === value)
    if (material) {
      const sgKey = pickKey(row.values, specificGravityKeys, 'specificgravity')
      if (material.density !== undefined) {
        row.values[sgKey] = material.density
      }
      if (material.price !== undefined) {
        const priceKey = pickKey(row.values, priceKeys, 'unitPrice')
        row.values[priceKey] = material.price
      }
    }
    updateMaterialCalc(row)
  }

  const updateProcessCalc = (row: CostRow) => {
    if (!row || row.section !== '加工成本') return
    if (!row.values) row.values = {}
    const v = row.values
    const rateKey = pickSectionKey('加工成本', v, processRateKeys, ['费率'])
    const qtyKey = pickSectionKey('加工成本', v, processQtyKeys, ['加工计量', '数量'])
    const feeKey = pickSectionKey('加工成本', v, processFeeKeys, ['加工费'])
    const rate = toNumber(v[rateKey])
    const qty = toNumber(v[qtyKey])
    v[feeKey] = Number((rate * qty).toFixed(4))
  }

  const handleStationSelect = (row: CostRow, value?: string) => {
    if (!row || !row.values) return
    const stationKey = pickSectionKey('加工成本', row.values, processStationKeys, ['加工工站'])
    row.values[stationKey] = value || ''
    const station = stationOptions.value.find((s) => s.value === value)
    if (station) {
      const rateKey = pickSectionKey('加工成本', row.values, processRateKeys, ['费率'])
      if (station.rate !== undefined) {
        row.values[rateKey] = station.rate
      }
      const unitKey = pickSectionKey('加工成本', row.values, processUnitKeys, ['单位'])
      if (station.unit) {
        row.values[unitKey] = station.unit
      }
    }
    updateProcessCalc(row)
  }

  const addCostRow = (section: string) => {
    const cols = mergeQuotationSectionColumns(section, current.templateSections)
    const values: Record<string, any> = {}
    const labels: Record<string, string> = {}
    cols.forEach((c) => {
      values[c.key] = ''
      labels[c.key] = c.label
    })
    const id = `r-${Date.now()}`
    costRows.value.push({ id, section, field: id, values, labels })
  }

  const removeCostRow = (id: string) => {
    costRows.value = costRows.value.filter((c) => c.id !== id)
  }

  function saveQuote() {
    if (dialog.quoteId && !isQuotationEditable(current)) {
      ElMessage.warning('仅未报价/报价中状态可保存')
      return
    }
    const c = (current.base.contact || '').trim()
    const p = (current.base.phone || '').trim()
    const e = (current.base.email || '').trim()
    if (!c || !p || !e) {
      ElMessage.warning('请填写完整【报价基础信息】后再保存。')
      return
    }
    ;(async () => {
      current.costItems = costItemsForCurrent.value
      current.quoteAmount = formatMoney(quoteTotal.value)
      loading.value = true
      try {
        const uploadedList = await Promise.all((current.attachments || []).map(uploadQuotationAttachmentFile))
        for (const f of uploadedList) {
          const path = String(f?.url ?? f?.file_path ?? '').trim()
          const name = String(f?.name ?? f?.file_name ?? '').trim()
          if (!name && !path) continue
          if (!path) {
            if (f?.raw) {
              ElMessage.error(`附件上传失败：${name || '未命名文件'}，请检查网络后重试`)
              return
            }
            ElMessage.error(`附件「${name || '未命名'}」缺少存储路径，请删除后重新上传`)
            return
          }
        }
        current.attachments = uploadedList
        const payload = buildSavePayload({ ...current, costItems: costItemsForCurrent.value })
        let res: any
        if (dialog.quoteId) {
          res = await api.update(dialog.quoteId, payload)
        } else {
          res = await api.create(payload)
        }
        const data = res?.data?.data ?? res?.data ?? res
        const updated = mapBackendQuote(data)
        await enrichQuotesWithInquiryData([updated])
        const idx = quotes.value.findIndex((q) => q.id === updated.id)
        if (idx >= 0) quotes.value.splice(idx, 1, updated)
        else quotes.value.unshift(updated)
        if (uiContext === 'detail') {
          options?.onSaveSuccess?.()
        } else {
          dialog.visible = false
        }
        ElMessage.success('已保存')
        options?.onChange?.()
      } catch (err) {
        console.error('保存报价失败', err)
        ElMessage.error('保存失败，请检查网络或必填项后重试')
      } finally {
        loading.value = false
      }
    })()
  }

  function submitQuotationFromRow(row: Quote) {
    if (!isQuotedQuotation(row)) {
      ElMessage.warning('仅报价中状态可提交报价')
      return
    }
    const bidReason = getSupplierBidWindowRejectReason(row)
    if (bidReason) {
      ElMessage.warning(bidReason)
      return
    }
    const c = (row.base?.contact || '').trim()
    const p = (row.base?.phone || '').trim()
    const e = (row.base?.email || '').trim()
    if (!c || !p || !e) {
      ElMessage.warning('请先将报价单中的【报价基础信息】填写完整后再提交报价。')
      return
    }
    if (!row.id) {
      ElMessage.warning('无法提交：缺少报价单标识')
      return
    }
    ;(async () => {
      loading.value = true
      try {
        const res: any = await api.submitOfficial(row.id)
        const raw = res?.data?.data ?? res?.data ?? res
        const inquiryClosed = raw?.inquiry_quote_closed === true
        const updated = mapBackendQuote(raw)
        await enrichQuotesWithInquiryData([updated])
        const idx = quotes.value.findIndex((q) => q.id === updated.id)
        if (idx >= 0) quotes.value.splice(idx, 1, updated)
        else quotes.value.unshift(updated)
        const tip =
          res?.data?.msg ||
          (inquiryClosed ? '报价已提交，询价单已进入报价结束' : '报价已提交')
        ElMessage.success(tip)
        options?.onChange?.()
      } catch (err) {
        console.error('提交报价失败', err)
        ElMessage.error('提交失败，请稍后重试')
      } finally {
        loading.value = false
      }
    })()
  }

  const clampField = (s: string, max: number) => (s || '').slice(0, max)

  /** 与后端 QuotationItem 一致：product_name≤20、unit≤10；缺省按料号主数据或料号/PCS 兜底 */
  const applyRfqItemsForPayload = (items: any[]) => {
    return items.map((raw) => {
      const it: any = { ...raw }
      const pid = String(it.part_id ?? it.partId ?? '').trim()
      const meta = pid ? miscPartByPartId.value[pid] : undefined
      let pn = String(it.product_name ?? it.productName ?? '').trim()
      let un = String(it.unit ?? '').trim()
      if (!pn && meta?.partid_name) pn = String(meta.partid_name).trim()
      if (!un && meta?.unit) un = String(meta.unit).trim()
      if (!pn && pid) pn = pid
      if (!un) un = 'PCS'
      delete it.partId
      delete it.productName
      it.part_id = pid || it.part_id
      it.product_name = clampField(pn, 20)
      it.unit = clampField(un, 10)
      return it
    })
  }

  const round4 = (n: number) => Number(n.toFixed(4))

  /** 将报价合计写入 BOM 行（is_bom=1）；无 BOM 时写入第一行，与单产品上阶明细场景一致 */
  const applyRfqItemsWithQuoteRollup = (items: any[]) => {
    const base = applyRfqItemsForPayload(items)
    if (!base.length) return base
    const r = quoteRollupForRfq.value
    const isBomLine = (it: any) => {
      const v = it.is_bom ?? it.IsBom
      return v === 1 || v === '1' || v === true
    }
    const targetIdxs = base.map((it, i) => i).filter((i) => isBomLine(base[i]))
    const idxs = targetIdxs.length ? targetIdxs : [0]
    const totals = {
      total_material_cost: round4(r.material),
      total_processing_cost: round4(r.processing),
      total_other_expense: round4(r.other),
      total_opex_amt: round4(r.opex),
      profit_rate: round4(r.profitAmt),
      tax_rate: round4(r.taxAmt),
      total_price_excl_tax: round4(r.preTax),
      total_price_incl_tax: round4(r.postTax)
    }
    for (const i of idxs) {
      const it = base[i]
      Object.assign(it, totals)
      const qty = Number(it.qty ?? 0)
      if (qty > 0 && r.postTax > 0) {
        it.unit_price = round4(r.postTax / qty)
      }
      it.product_cost = round4(r.postTax)
    }
    return base
  }

  /** 可选整数：空不提交；0 合法（勿用 `|| undefined` 误丢 0） */
  const optionalIntForPayload = (v: string | number | null | undefined) => {
    if (v === '' || v == null) return undefined
    const n = typeof v === 'number' ? v : Number(String(v).trim())
    return Number.isFinite(n) ? n : undefined
  }

  /** 弹窗保存：与后端约定不提交 status / quotetime（由列表「提交报价」接口写入） */
  const buildSavePayload = (q: Quote) => {
    const nested = costRowsToNestedPayload(costRows.value)
    const defaultPartId =
      (Array.isArray(q.rfqItems) && q.rfqItems[0] && (q.rfqItems[0].part_id || q.rfqItems[0].partId)) || ''
    if (defaultPartId) {
      const fillPart = (rows: any[]) =>
        rows.map((row) =>
          !row.part_id || !String(row.part_id).trim() ? { ...row, part_id: defaultPartId } : row
        )
      nested.material_costs = fillPart(nested.material_costs)
      nested.process_costs = fillPart(nested.process_costs)
      nested.other_costs = fillPart(nested.other_costs)
      nested.profit_costs = fillPart(nested.profit_costs)
    }
    const attachmentRows = buildQuotationAttachmentsForSave(q.attachments, defaultPartId)
    // 仅提交 QuotationMaster / 嵌套子表存在的字段（询价标题、模板、币别等由询价主表维护，不在报价主表模型上）
    const payload: any = {
      quotation_no: q.quoteNo || undefined,
      inquiry_no: q.inquiryCode || undefined,
      quote_deadline: quoteDeadlineToApiPayload(q.quoteDeadline),
      supplier_code: q.supplierCode || undefined,
      supplier_name: q.supplierName || undefined,
      contact_person: q.base.contact || undefined,
      contact_phone: q.base.phone || undefined,
      contact_email: q.base.email || undefined,
      validity_days: optionalIntForPayload(q.base.validityDays),
      delivery_days: optionalIntForPayload(q.base.leadTimeDays),
      payment_method: paymentMapFrontToBackend[q.base.paymentTerm] || undefined,
      /** 与 QuotationMasterCreateUpdateSerializer 一致，写入 material_costs 等子表 */
      material_costs: nested.material_costs,
      process_costs: nested.process_costs,
      other_costs: nested.other_costs,
      profit_costs: nested.profit_costs,
      attachments: attachmentRows,
      remark: q.remark || ''
    }
    if (Array.isArray(q.rfqItems) && q.rfqItems.length) {
      payload.rfq_items = applyRfqItemsWithQuoteRollup(q.rfqItems)
    }
    return payload
  }

  /** 与主表 `QuotationMaster.status` 一致：仅 1（未报价）可编辑/提交 */
  function isPendingQuotation(q: Quote | Record<string, any>) {
    const row = q as any
    const fromCode = Number(row.statusCode)
    if (Number.isFinite(fromCode)) return fromCode === 1 || fromCode === 2
    const fromRaw = Number(row.status)
    if (Number.isFinite(fromRaw)) return fromRaw === 1 || fromRaw === 2
    return row.status === 'pending'
  }

  function isQuotedQuotation(q: Quote | Record<string, any>) {
    const row = q as any
    const fromCode = Number(row.statusCode)
    if (Number.isFinite(fromCode)) return fromCode === 2
    const fromRaw = Number(row.status)
    if (Number.isFinite(fromRaw)) return fromRaw === 2
    return row.status === 'quoted'
  }

  function isQuotationEditable(q: Quote | Record<string, any>) {
    return isPendingQuotation(q) || isQuotedQuotation(q)
  }

  const templateLabel = (t: string) => {
    if (t == null || t === '') return ''
    const key = String(t).trim()
    const fromDb = templateNameByCode.value[key]
    if (fromDb) return fromDb
    const legacy: Record<string, string> = { tooling: '模治具', equipment: '设备', plastic: '塑胶件' }
    return legacy[key] || key
  }
  const statusLabel = (s: QuoteStatus) => ({
    pending: '待报价',
    quoted: '报价中',
    completed: '已报价',
    expired: '已过期'
  }[s] || s)

  const statusTagType = (s: QuoteStatus) => ({
    pending: 'warning',
    quoted: 'primary',
    completed: 'success',
    expired: 'info'
  }[s] || 'info')

  return {
    filters,
    statusOptions,
    resetFilter,
    filteredQuotes,
    loading,
    loadQuotes,
    isPendingQuotation,
    isQuotedQuotation,
    isQuotationEditable,
    viewQuote,
    openQuote,
    dialog,
    dialogTitle: computed(() => (dialog.mode === 'view' ? '查看报价' : dialog.quoteId ? '编辑报价' : '新增报价')),
    statusTagType,
    statusLabel,
    templateLabel,
    current,
    isReadOnly: computed(() => dialog.mode === 'view'),
    isCostCellDisabled,
    groupedCostRows,
    sectionColumns,
    sectionAddConfig,
    primarySections,
    profitTaxSections,
    loadCostRowsFromTemplate,
    quoteSummaryRows,
    quoteAmountPreTax,
    quoteTotal,
    addCostRow,
    removeCostRow,
    materialOptions,
    materialLoading,
    stationOptions,
    stationLoading,
    unitOptions,
    unitLoading,
    handleMaterialSelect,
    handleStationSelect,
    updateMaterialCalc,
    updateProcessCalc,
    weightKeys,
    materialFeeKeys,
    processUnitKeys,
    processRateKeys,
    processFeeKeys,
    formatMoney,
    saveQuote,
    submitQuotationFromRow
  }
}

const buildCostItems = (templateKey: string, templateSections?: any, enableCostStructure = true): CostItem[] => {
  const fromTplSections = buildCostItemsFromTemplateSections(templateSections, enableCostStructure)
  if (fromTplSections.length) return fromTplSections
  if (!enableCostStructure) return buildDefaultNonBomCostItems()
  const tpl = resolveTemplate(templateKey)
  const allowed = new Set(enableCostStructure ? costEnabledSections : costDisabledSections)
  return tpl
    .filter((item) => allowed.has(item.section))
    .map((item) => ({
      id: crypto.randomUUID(),
      section: item.section,
      span: item.span,
      attrs: item.attrs.map((a) => ({ ...a }))
    }))
}
