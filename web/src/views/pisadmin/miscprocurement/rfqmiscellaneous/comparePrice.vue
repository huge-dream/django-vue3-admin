<template>
  <fs-page class="compare-price-page" :class="{ 'compare-price-page--public-share': isPublicShare }" v-loading="comparisonDialog.loading">
    <template #header>
      <header v-if="!isPublicShare" class="compare-price-toolbar">
        <div class="compare-price-toolbar__left">
          <el-button text class="compare-price-back" @click="goBack">
            <el-icon class="compare-price-back__icon"><ArrowLeft /></el-icon>
            返回
          </el-button>
          <h1 class="compare-price-toolbar__title">{{ pageTitle }}</h1>
        </div>
      </header>
    </template>

    <div class="compare-price-body">
      <div class="compare-body">
        <div class="compare-info">
          <div class="info-item"><span class="label">询价单号</span><span class="value">{{ displayTextEmpty(comparisonDialog.baseInfo.code) }}</span></div>
          <div class="info-item"><span class="label">采购件料号</span><span class="value">{{ displayTextEmpty(comparisonDialog.baseInfo.partNo) }}</span></div>
          <div class="info-item"><span class="label">采购件名称</span><span class="value">{{ displayTextEmpty(comparisonDialog.baseInfo.partName) }}</span></div>
          <div class="info-item"><span class="label">目标价格</span><span class="value">{{ compareNumericDisplay(comparisonDialog.baseInfo.targetPrice) }}</span></div>
          <div class="info-item"><span class="label">交易币别</span><span class="value">{{ displayTextEmpty(comparisonDialog.baseInfo.currency) }}</span></div>
          <div class="info-item"><span class="label">税率</span><span class="value">{{ displayPercentRate(comparisonDialog.baseInfo.taxRate) }}</span></div>
          <div class="info-item"><span class="label">当前成交价</span><span class="value">{{ compareNumericDisplay(comparisonDialog.baseInfo.dealPrice) }}</span></div>
          <div class="info-item"><span class="label">制程最低价</span><span class="value">{{ compareNumericDisplay(comparisonDialog.baseInfo.lowestProcessPrice) }}</span></div>
        </div>

        <el-table
          :key="compareTableRenderKey"
          ref="compareTableRef"
          :data="comparisonDialog.rows"
          border
          size="small"
          class="compare-table"
          :row-key="comparisonRowKeyFn"
          :row-class-name="comparisonRowClassName"
          @expand-change="handleComparisonExpandChange"
        >
          <el-table-column type="expand" width="1" class-name="hidden-expand" header-class-name="hidden-expand">
            <template #default="{ row: parentRow }">
              <div class="compare-detail">
                <template v-if="parentRow.detailGroups && parentRow.detailGroups.length">
                  <div v-for="grp in parentRow.detailGroups" :key="grp.title" class="compare-detail-group">
                    <div class="compare-detail-group-title">{{ grp.title }}</div>
                    <el-table :data="grp.lines" size="small" border class="compare-detail-table" :show-header="false" >
                      <el-table-column label="明细" prop="label" min-width="140" />
                      <el-table-column
                        v-for="(sup, supIdx) in comparisonDialog.suppliers"
                        :key="`${grp.title}-${sup.name}`"
                        :prop="`values.${sup.name}`"
                        min-width="120"
                      >
                        <template #header>
                          <span class="supplier-header-link" title="查看报价单详情" @click.stop="openQuotationPreview(supIdx)">
                            {{ sup.name }}
                          </span>
                        </template>
                        <template #default="{ row: line }">
                          <span :class="['compare-value', line.min === line.values[sup.name] ? 'is-min' : '']">
                            {{ formatMetricDetailCell(line.values[sup.name], line.label, line.isText) }}
                          </span>
                        </template>
                      </el-table-column>
                      <el-table-column prop="avg" label="平均价" width="100">
                        <template #default="{ row: line }">
                          <span v-if="parentRow.key === 'process'"> </span>
                          <span v-else>{{ formatCompareAvg(line.avg, parentRow.key, line.label) }}</span>
                        </template>
                      </el-table-column>
                      <el-table-column prop="min" label="制程最低价" width="110">
                        <template #default="{ row: line }">
                          <template v-if="parentRow.key === 'process'">
                            <span> </span>
                          </template>
                          <template v-else>
                            <el-tooltip
                              v-if="
                                line.minLink?.kind === 'misc_materials' &&
                                line.minLink.sourceFactory
                              "
                              placement="top"
                              effect="dark"
                            >
                              <template #content>
                                <div class="material-min-split-tooltip">来源厂区：{{ line.minLink.sourceFactory }}</div>
                              </template>
                              <span class="compare-min-link" @click.stop="openCompareMinLink(line.minLink)">
                                {{ formatCompareMin(line.min, parentRow.key, line.label) }}
                              </span>
                            </el-tooltip>
                            <span
                              v-else-if="line.minLink?.kind === 'quotation' || line.minLink?.kind === 'misc_materials'"
                              class="compare-min-link"
                              @click.stop="openCompareMinLink(line.minLink)"
                            >
                              {{ formatCompareMin(line.min, parentRow.key, line.label) }}
                            </span>
                            <span v-else>{{ formatCompareMin(line.min, parentRow.key, line.label) }}</span>
                          </template>
                        </template>
                      </el-table-column>
                    </el-table>
                  </div>
                </template>
                <!-- <el-table
                  v-else-if="row.details && row.details.length"
                  :data="row.details"
                  size="small"
                  border
                  class="compare-detail-table"
                >
                  <el-table-column :label="detailHeaderLabel(row)" prop="label" min-width="140" />
                  <el-table-column
                    v-for="(sup, supIdx) in comparisonDialog.suppliers"
                    :key="sup.name"
                    :prop="`values.${sup.name}`"
                    min-width="140"
                  >
                    <template #header>
                      <span class="supplier-header-link" title="查看报价单详情" @click.stop="openQuotationPreview(supIdx)">
                        {{ sup.name }}
                      </span>
                    </template>
                    <template #default="{ row: detail }">
                      <span :class="['compare-value', detail.min === detail.values[sup.name] ? 'is-min' : '']">
                        {{ formatMetricDetailCell(detail.values[sup.name], detail.label, detail.isText) }}
                      </span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="avg" label="平均价" width="120">
                    <template #default="{ row: detail }">{{ formatCompareAvg(detail.avg, row.key) }}</template>
                  </el-table-column>
                  <el-table-column prop="min" label="制程最低价" width="120">
                    <template #default="{ row: detail }">
                      <el-tooltip
                        v-if="
                          detail.minLink?.kind === 'misc_materials' &&
                          detail.minLink.sourceFactory
                        "
                        placement="top"
                        effect="dark"
                      >
                        <template #content>
                          <div class="material-min-split-tooltip">来源厂区：{{ detail.minLink.sourceFactory }}</div>
                        </template>
                        <span class="compare-min-link" @click.stop="openCompareMinLink(detail.minLink)">
                          {{ formatCompareMin(detail.min, row.key) }}
                        </span>
                      </el-tooltip>
                      <span
                        v-else-if="detail.minLink?.kind === 'quotation' || detail.minLink?.kind === 'misc_materials'"
                        class="compare-min-link"
                        @click.stop="openCompareMinLink(detail.minLink)"
                      >
                        {{ formatCompareMin(detail.min, row.key) }}
                      </span>
                      <span v-else>{{ formatCompareMin(detail.min, row.key) }}</span>
                    </template>
                  </el-table-column>
                </el-table> -->
                <div v-else class="no-detail">暂无明细</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="label" label="成本结构" fixed="left" min-width="160">
            <template #default="{ row }">
              <span
                v-if="(row.details && row.details.length) || (row.detailGroups && row.detailGroups.length)"
                class="expand-toggle"
                @click.stop="toggleCompareExpand(row)"
              >
                {{ expandedRowKeys.includes(comparisonRowKeyFn(row)) ? '－' : '＋' }}
              </span>
              <span>{{ row.label }}</span>
            </template>
          </el-table-column>
          <el-table-column
            v-for="(sup, supIdx) in comparisonDialog.suppliers"
            :key="sup.name"
            :prop="`values.${sup.name}`"
            min-width="140"
          >
            <template #header>
              <span class="supplier-header-link" title="查看报价单详情" @click.stop="openQuotationPreview(supIdx)">
                {{ sup.name }}
              </span>
            </template>
            <template #default="{ row }">
              <template v-if="row.key === 'bargain'">
                <span v-if="isPublicShare" class="compare-readonly-cell">{{ formatBargainDisplayReadonly(row.values[sup.name]) }}</span>
                <el-input v-else v-model="row.values[sup.name]" size="small" placeholder="请输入议价价" />
              </template>
              <template v-else-if="row.key === 'award'">
                <span v-if="isPublicShare" class="compare-readonly-cell">{{ displayTextEmpty(row.values[sup.name]) }}</span>
                <el-switch
                  v-else
                  :model-value="row.values[sup.name] === '是'"
                  @update:model-value="(val: boolean) => toggleComparisonAward(row, sup.name, val)"
                  active-text="是"
                  inactive-text="否"
                />
              </template>
              <template v-else-if="row.key === 'profit'">
                <span :class="['compare-value', row.min === row.values[sup.name] ? 'is-min' : '']">
                  {{ formatComparisonMainCell(row, row.values[sup.name]) }}<template v-if="row.profitMarginPctBySupplier?.[sup.name]">（利润率：{{ row.profitMarginPctBySupplier[sup.name] }}）</template>
                </span>
              </template>
              <template v-else>
                <span :class="['compare-value', row.min === row.values[sup.name] ? 'is-min' : '']">
                  {{ formatComparisonMainCell(row, row.values[sup.name]) }}
                </span>
              </template>
            </template>
          </el-table-column>
          <el-table-column prop="avg" label="平均价" width="120">
            <template #default="{ row }">{{ row.key === 'bargain' ? '-' : formatCompareAvg(row.avg, row.key) }}</template>
          </el-table-column>
          <el-table-column prop="min" label="制程最低价" width="120">
            <template #default="{ row }">
              <template v-if="row.key === 'bargain'">-</template>
              <template
                v-else-if="row.key === 'process' && row.minLink?.kind === 'quotation'"
              >
                <span class="compare-min-link" @click.stop="openCompareMinLink(row.minLink)">
                  {{ formatCompareMin(row.min, row.key) }}
                </span>
              </template>
              <template v-else-if="row.key === 'profit'">
                {{ formatCompareMin(row.min, row.key)
                }}<template v-if="row.profitMinMarginDisplay">（利润率：{{ row.profitMinMarginDisplay }}）</template>
              </template>
              <template v-else>{{ formatCompareMin(row.min, row.key) }}</template>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <template v-if="!isPublicShare" #footer>
      <div class="compare-price-footer">
        <el-button @click="onSaveComparisonDraft" :loading="comparisonDialog.loading" :disabled="![4, 5, 6].includes(comparisonInquiryStatus)">暂存</el-button>
        <el-button
          type="success"
          @click="onConfirmComparison"
          :loading="comparisonDialog.loading"
          :disabled="![4, 5, 6].includes(comparisonInquiryStatus)"
        >
          确认比价
        </el-button>
        <el-button
          type="primary"
          @click="onSubmitComparisonReview"
          :loading="comparisonDialog.loading"
          :disabled="comparisonInquiryStatus !== 7"
        >
          提交核价
        </el-button>
      </div>
    </template>
  </fs-page>
</template>

<script setup lang="ts" name="RfqMiscComparePrice">
import { ArrowLeft } from '@element-plus/icons-vue'
import { computed, nextTick, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getList as getQuotationList,
  getDetail as getQuotationDetail,
  update as updateQuotation
} from '../../../pissupplier/quotation/api'
import {
  formatRfqApiErrorMessage,
  displayTextEmpty,
  displayPercentRate,
  COMPARE_PRICE_MATERIAL_DETAIL_METRICS,
  COMPARE_PRICE_PROCESS_DETAIL_METRICS,
  shouldSkipMaterialDetailMetric,
  shouldSkipProcessDetailMetric,
  computeLowPriceMinContext,
  applyMaterialDetailLowPriceMin,
  buildMaterialCostMinLink,
  allCompareSupplierValuesEqual,
  formatQuotationProfitMarginForCompare,
  computeProfitProcessMinPrice,
  formatMinProfitMarginForCompare,
  computeTaxProcessMinPrice,
  sumComparisonProcessMinTotals,
  sumComparisonAverageTotals,
  computeProfitRowAveragePrice,
  computeTaxRowAveragePrice,
  coalesceCompareNumeric,
  type CompareMinLink,
  type ComparisonDetailMetric,
  type LowPriceMinContext
} from './crud'
import * as api from './api'
import { GetList as GetMaterials } from '../misc_materials/api'
import { GetList as GetStations } from '../misc_stations/api'

const route = useRoute()
const router = useRouter()

/** 对外分享路由：免登录，只读（``?inquiry_id=`` 询价单主键） */
const isPublicShare = computed(
  () =>
    route.name === 'PublicMiscComparePrice' || String(route.path || '').includes('/public/misc-compare')
)

const unwrapInquiryDetail = (res: any) => res?.data?.data ?? res?.data ?? res

const goBack = () => {
  router.back()
}

const formatBargainDisplayReadonly = (v: unknown) => formatBargainDisplayValue(v)

type ComparisonDetailRow = {
  label: string
  values: Record<string, any>
  avg?: number
  min?: number
  /** 制程最低价列：重量/单价行跳转（报价单详情或杂采材料管理） */
  minLink?: CompareMinLink | null
  /** 与成本模板字段一致：文本列走 displayTextEmpty */
  isText?: boolean
}
/** 材料/加工：按材质或工站分组，组内多行明细（对齐 bargain_price.html 展开结构） */
type ComparisonDetailGroup = { title: string; lines: ComparisonDetailRow[] }
type ComparisonRow = ComparisonDetailRow & {
  key: string
  details?: ComparisonDetailRow[]
  detailGroups?: ComparisonDetailGroup[]
  /** 利润行：各供应商列括号内利润率文案（与 QuotationProfit.profit_rate 一致） */
  profitMarginPctBySupplier?: Record<string, string>
  /** 制程最低价列：利润行末尾「利润率：x%」（取各报价最小利润率） */
  profitMinMarginDisplay?: string
}

const compareTableRef = ref()
/** el-table 内 el-input 在异步合并 values 后常不重绘，递增 key 强制刷新 */
const compareTableRenderKey = ref(0)
const expandedRowKeys = ref<string[]>([])

const comparisonDialog = reactive({
  loading: false,
  currentRow: null as any,
  quotes: [] as any[],
  baseInfo: {
    code: '',
    partNo: '',
    partName: '',
    targetPrice: '',
    currency: '',
    taxRate: '',
    dealPrice: '',
    lowestProcessPrice: ''
  },
  suppliers: [] as { name: string; code: string; quotationId?: number | string }[],
  rows: [] as ComparisonRow[]
})

const pageTitle = computed(() => {
  const row = comparisonDialog.currentRow
  const suffix = row?.title || row?.inquiry_name || row?.inquiry_no || ''
  return suffix ? `比价/议价 - ${suffix}` : '比价/议价'
})

/** 打开报价单详情路由页（默认查看模式，与供应商端详情页一致；分享模式下走公开路由） */
const openQuotationPreview = (supplierIndex: number) => {
  const quote: any = comparisonDialog.quotes[supplierIndex]
  const sup = comparisonDialog.suppliers[supplierIndex]
  const id = sup?.quotationId ?? quote?.autoid ?? quote?.id
  if (id == null || id === '') {
    ElMessage.warning('暂无该供应商报价单数据')
    return
  }
  if (isPublicShare.value) {
    router.push({
      name: 'PublicPissupplierQuotationShare',
      query: { id: String(id) }
    })
    return
  }
  router.push({
    name: 'PissupplierQuotationDetail',
    params: { id: String(id) }
  })
}

/** 展开表「制程最低价」列：重量/单价行跳转 */
const openCompareMinLink = (link: CompareMinLink) => {
  if (link.kind === 'material_cost_split') return
  if (link.kind === 'quotation') {
    if (isPublicShare.value) {
      router.push({
        name: 'PublicPissupplierQuotationShare',
        query: { id: String(link.id) }
      })
      return
    }
    router.push({
      name: 'PissupplierQuotationDetail',
      params: { id: String(link.id) }
    })
  } else {
    router.push({ name: 'PisadminMiscMaterialsIndex' })
  }
}

const comparisonInquiryStatus = computed(() => Number(comparisonDialog.currentRow?.status))

/** 比价页数值统一保留小数位（表头、主表、展开明细）；「比重」明细除外 */
const COMPARE_DECIMAL_PLACES = 4

const compareNumericDisplay = (v: unknown): string => {
  if (v === null || v === undefined || v === '' || v === '-') return `0.${'0'.repeat(COMPARE_DECIMAL_PLACES)}`
  const n = Number(v)
  if (Number.isFinite(n)) return n.toFixed(COMPARE_DECIMAL_PLACES)
  const s = String(v).trim()
  return s === '' ? `0.${'0'.repeat(COMPARE_DECIMAL_PLACES)}` : s
}

const isSpecificGravityDetailLabel = (label: unknown) => String(label ?? '').trim() === '比重'

/** 「比重」：不四舍五入补位，直接展示接口/库中原样（字符串或数字转字符串） */
const formatSpecificGravityRaw = (v: unknown): string => {
  if (v === null || v === undefined || v === '') return '-'
  const s = String(v).trim()
  return s === '' ? '-' : s
}

/** 比价主表：利润/税金等为数值；不加 %（表头「税率」用 displayPercentRate） */
const formatComparisonMainCell = (row: ComparisonRow, v: unknown) => {
  if (row.key === 'rank') {
    if (v === null || v === undefined || v === '') return '-'
    return String(v)
  }
  if (v === null || v === undefined || v === '' || v === '-') return `0.${'0'.repeat(COMPARE_DECIMAL_PLACES)}`
  const n = Number(v)
  if (Number.isFinite(n)) return n.toFixed(COMPARE_DECIMAL_PLACES)
  return String(v)
}

const formatCompareAvg = (v: unknown, _rowKey?: string, detailLabel?: string) => {
  if (isSpecificGravityDetailLabel(detailLabel)) {
    if (v === undefined || v === null) return '-'
    const n = Number(v)
    return Number.isFinite(n) ? n.toFixed(COMPARE_DECIMAL_PLACES) : String(v)
  }
  if (v === undefined || v === null) return `0.${'0'.repeat(COMPARE_DECIMAL_PLACES)}`
  const n = Number(v)
  if (Number.isFinite(n)) return n.toFixed(COMPARE_DECIMAL_PLACES)
  return String(v)
}

const formatCompareMin = (v: unknown, _rowKey?: string, detailLabel?: string) => {
  if (isSpecificGravityDetailLabel(detailLabel)) {
    if (v === undefined || v === null) return '-'
    const n = Number(v)
    return Number.isFinite(n) ? n.toFixed(COMPARE_DECIMAL_PLACES) : String(v)
  }
  if (v === undefined || v === null) return `0.${'0'.repeat(COMPARE_DECIMAL_PLACES)}`
  const n = Number(v)
  if (Number.isFinite(n)) return n.toFixed(COMPARE_DECIMAL_PLACES)
  return String(v)
}

/** 材料成本分项浮窗：与制程最低价列数字格式一致 */
const formatMaterialSplitTooltipNumber = (v: number) => {
  if (!Number.isFinite(v)) return '—'
  return v.toFixed(COMPARE_DECIMAL_PLACES)
}

const extractQuotationList = (res: any): any[] => {
  const raw = res?.data?.results ?? res?.data?.data?.results ?? res?.data?.list ?? res?.data
  return Array.isArray(raw) ? raw : []
}

/** 工站代码 → 工站名称（与 pis_misc_procurement_station_info 一致） */
const fetchStationCodeToNameMap = async (): Promise<Record<string, string>> => {
  const map: Record<string, string> = {}
  try {
    const res = await GetStations({ page: 1, page_size: 5000, pageSize: 5000 })
    const list = extractQuotationList(res)
    for (const row of list) {
      const code = String(row.stationcode ?? row.station_code ?? '').trim()
      const name = String(row.stationname ?? row.station_name ?? '').trim()
      if (code && name) map[code] = name
    }
  } catch {
    /* 主数据不可用时仍显示库中工站代码 */
  }
  return map
}

/** 与 fetchStationCodeToNameMap 同逻辑，供分享数据包内嵌工站列表使用 */
const buildStationMapFromList = (list: any[]): Record<string, string> => {
  const map: Record<string, string> = {}
  for (const row of list || []) {
    const code = String(row.stationcode ?? row.station_code ?? '').trim()
    const name = String(row.stationname ?? row.station_name ?? '').trim()
    if (code && name) map[code] = name
  }
  return map
}

const processStationGroupTitle = (stationKey: string, stationNameByCode?: Record<string, string>) => {
  const t = String(stationKey || '').trim()
  if (t === '工站') return '工站'
  if (!t) return '工站'
  const name = stationNameByCode?.[t]
  return name || t
}

const unwrapQuotationDetail = (res: any) => {
  const d = res?.data
  if (d && typeof d === 'object' && d.data != null) return d.data
  return d
}

const quotationSupplierKey = (quote: any, idx: number) =>
  quote?.supplier_name ||
  quote?.supplierName ||
  quote?.supplier_code ||
  quote?.supplierCode ||
  quote?.autoid ||
  quote?.id ||
  `sup-${idx}`

/** 议价金额回显：保留接口字符串精度，避免 Number 化丢小数位 */
const formatBargainDisplayValue = (bp: any): string => {
  if (bp === null || bp === undefined || bp === '') return ''
  if (typeof bp === 'string') {
    const t = bp.trim()
    return t
  }
  const n = Number(bp)
  if (Number.isFinite(n)) return String(n)
  return String(bp)
}

const hasBargainPrice = (bp: any): boolean => {
  if (bp === null || bp === undefined || bp === '') return false
  if (typeof bp === 'number') return Number.isFinite(bp)
  const n = Number(bp)
  return Number.isFinite(n) || (typeof bp === 'string' && bp.trim() !== '')
}

const mergeNegotiationIntoComparisonRows = (
  rows: ComparisonRow[],
  quotes: any[],
  negList: any[]
) => {
  if (!Array.isArray(negList) || !negList.length) return
  const byQuotationNo = new Map<string, any>()
  const byCode = new Map<string, any>()
  negList.forEach((r) => {
    const qn = String(r.quotation_no || '').trim()
    const c = String(r.supplier_code || '').trim()
    if (qn) byQuotationNo.set(qn, r)
    if (c) byCode.set(c, r)
  })
  const bargainRow = rows.find((r) => r.key === 'bargain')
  const awardRow = rows.find((r) => r.key === 'award')
  const keys = quotes.map((q, idx) => quotationSupplierKey(q, idx))
  const bargainNext = bargainRow?.values ? { ...bargainRow.values } : {}
  const awardNext = awardRow?.values ? { ...awardRow.values } : {}
  quotes.forEach((quote, idx) => {
    const qn = String(quote.quotation_no || quote.quotationNo || '').trim()
    const code = String(quote.supplier_code || quote.supplierCode || '').trim()
    const rec = (qn && byQuotationNo.get(qn)) || (code ? byCode.get(code) : null)
    if (!rec) return
    const name = keys[idx]
    const bp = rec.bargaining_price
    bargainNext[name] = hasBargainPrice(bp) ? formatBargainDisplayValue(bp) : ''
    awardNext[name] = Number(rec.is_awarded) === 1 ? '是' : '否'
  })
  if (bargainRow) bargainRow.values = bargainNext
  if (awardRow) awardRow.values = awardNext
}

/** 合并议价数据后整体替换行引用，避免 el-table 单元格内 el-input 不随异步赋值更新 */
const applyComparisonRowsAfterNegotiationMerge = async (rows: ComparisonRow[]) => {
  comparisonDialog.rows = rows.map((r) => ({
    ...r,
    values: { ...r.values },
    details: r.details ? r.details.map((d) => ({ ...d, values: { ...d.values } })) : undefined,
    detailGroups: r.detailGroups
      ? r.detailGroups.map((g) => ({
          ...g,
          lines: g.lines.map((l) => ({ ...l, values: { ...l.values } }))
        }))
      : undefined
  }))
  await nextTick()
  compareTableRenderKey.value += 1
}

const calcCompareStats = (values: Record<string, any>) => {
  const nums = Object.values(values || {})
    .map((v: any) => Number(v))
    .filter((v): v is number => Number.isFinite(v))
  if (!nums.length) return { avg: undefined as number | undefined, min: undefined as number | undefined }
  return {
    avg: nums.reduce((a, b) => a + b, 0) / nums.length,
    min: Math.min(...nums)
  }
}

const sumMaterialCost = (q: any): number | null => {
  const rows = q.material_costs || []
  let s = 0
  let ok = false
  for (const r of rows) {
    const n = Number(r.material_cost)
    if (Number.isFinite(n)) {
      s += n
      ok = true
    }
  }
  if (ok) return s
  let s2 = 0
  let ok2 = false
  for (const it of q.rfq_items || []) {
    const n = Number(it.total_material_cost)
    if (Number.isFinite(n)) {
      s2 += n
      ok2 = true
    }
  }
  return ok2 ? s2 : null
}

const sumProcessCost = (q: any): number | null => {
  let s = 0
  let ok = false
  for (const r of q.process_costs || []) {
    const n = Number(r.process_price)
    if (Number.isFinite(n)) {
      s += n
      ok = true
    }
  }
  if (ok) return s
  let s2 = 0
  let ok2 = false
  for (const it of q.rfq_items || []) {
    const n = Number(it.total_processing_cost)
    if (Number.isFinite(n)) {
      s2 += n
      ok2 = true
    }
  }
  return ok2 ? s2 : null
}

const sumOtherCost = (q: any): number | null => {
  let s = 0
  let ok = false
  for (const r of q.other_costs || []) {
    const a = Number(r.packaging_cost)
    const b = Number(r.transportation_cost)
    if (Number.isFinite(a)) {
      s += a
      ok = true
    }
    if (Number.isFinite(b)) {
      s += b
      ok = true
    }
  }
  if (ok) return s
  let s2 = 0
  let ok2 = false
  for (const it of q.rfq_items || []) {
    const n = Number(it.total_other_expense)
    if (Number.isFinite(n)) {
      s2 += n
      ok2 = true
    }
  }
  return ok2 ? s2 : null
}

const sumRfqField = (q: any, field: string): number | null => {
  let s = 0
  let ok = false
  for (const it of q.rfq_items || []) {
    const n = Number(it[field])
    if (Number.isFinite(n)) {
      s += n
      ok = true
    }
  }
  return ok ? s : null
}

const firstRfqField = (q: any, field: string) => {
  const it = (q.rfq_items || [])[0]
  if (!it) return undefined
  const v = it[field]
  return v !== undefined && v !== null && v !== '' ? v : undefined
}

/** 与上阶物料料号对齐的 `profit_costs` 行，供利润率括号展示 */
const profitCostRowForQuote = (q: any) => {
  const it = (q.rfq_items || [])[0]
  const pid = it ? String(it.part_id ?? '').trim() : ''
  const list = Array.isArray(q.profit_costs) ? q.profit_costs : []
  if (pid) {
    const hit = list.find((p: any) => String(p.part_id ?? '').trim() === pid)
    if (hit) return hit
  }
  return list[0]
}

/** 与比价表「总价」行一致，用于按含税总价排名（价低名次靠前） */
const getQuoteTotalNumeric = (q: any): number | null => {
  const a = q?.quote_amount
  if (a !== undefined && a !== null && a !== '') {
    const n = Number(a)
    if (Number.isFinite(n)) return n
  }
  const s = sumRfqField(q, 'total_price_incl_tax')
  if (s != null && Number.isFinite(s)) return s
  return null
}

/** 按总价升序赋名次；同价同名次（1,1,3）；无有效总价显示为 '-' */
const buildRanksByTotal = (quotes: any[], supplierKeys: string[]): Record<string, any> => {
  const out: Record<string, any> = {}
  supplierKeys.forEach((k) => {
    out[k] = '-'
  })
  const entries = supplierKeys
    .map((key, idx) => ({ key, total: getQuoteTotalNumeric(quotes[idx]) }))
    .filter((e): e is { key: string; total: number } => e.total != null && Number.isFinite(e.total))
  entries.sort((a, b) => a.total - b.total)
  let rank = 1
  for (let i = 0; i < entries.length; i++) {
    if (i > 0 && entries[i].total !== entries[i - 1].total) {
      rank = i + 1
    }
    out[entries[i].key] = rank
  }
  return out
}

/** 合并 option_json 扁平字段，便于带出模板扩展列 */
const mergeOptionJsonIntoRow = (row: any): any => {
  if (!row || typeof row !== 'object') return row
  const oj = row.option_json
  if (oj == null || oj === '') return row
  let extra: Record<string, any> = {}
  if (typeof oj === 'string') {
    try {
      const p = JSON.parse(oj)
      if (p && typeof p === 'object') extra = p
    } catch {
      return row
    }
  } else if (typeof oj === 'object') {
    extra = oj as Record<string, any>
  }
  return { ...row, ...extra }
}

/** 比价展开明细：按行标签区分数值与文本；比重行展示库表原值 */
const formatMetricDetailCell = (v: unknown, label: string, isText?: boolean) => {
  if (isText === true || label === '备注') return displayTextEmpty(v)
  if (isSpecificGravityDetailLabel(label)) return formatSpecificGravityRaw(v)
  return compareNumericDisplay(v)
}

const formatMetricCell = (v: unknown, isText: boolean, metricLabel?: string) => {
  if (isText) return displayTextEmpty(v)
  if (isSpecificGravityDetailLabel(metricLabel)) return formatSpecificGravityRaw(v)
  return compareNumericDisplay(v)
}

const findMaterialRowBySpec = (q: any, spec: string) => {
  const t = String(spec || '').trim()
  return (q.material_costs || []).find((r: any) => String(r.material_spec || '').trim() === t)
}

const findProcessRowByStation = (q: any, station: string) => {
  const t = String(station || '').trim()
  return (q.process_costs || []).find((r: any) => String(r.process_station || '').trim() === t)
}

/** 材料成本展开：按材料规格分组；「制程最低价」列对每个材质分组单独计算最低价 */
const buildMaterialDetailGroups = (
  quotes: any[],
  supplierKeys: string[],
  metrics: ComparisonDetailMetric[] = COMPARE_PRICE_MATERIAL_DETAIL_METRICS,
  lowPriceCtx: LowPriceMinContext | null = null
): ComparisonDetailGroup[] => {
  const specs = new Set<string>()
  quotes.forEach((q) => {
    ;(q.material_costs || []).forEach((r: any) => {
      specs.add(String(r.material_spec || '').trim() || '材料')
    })
  })
  const sortedSpecs = [...specs].sort()
  const groups: ComparisonDetailGroup[] = []
  for (const spec of sortedSpecs) {
    const lines: ComparisonDetailRow[] = []
    for (const m of metrics) {
      if (shouldSkipMaterialDetailMetric(m.fieldKey)) continue
      const values: Record<string, any> = {}
      supplierKeys.forEach((sup, idx) => {
        const raw = findMaterialRowBySpec(quotes[idx], spec)
        const merged = mergeOptionJsonIntoRow(raw || {})
        values[sup] = formatMetricCell(m.get(merged), m.isText, m.label)
      })
      const allDash = supplierKeys.every((sup) => values[sup] === '-')
      if (allDash) continue
      const line: ComparisonDetailRow = { label: m.label, values, isText: m.isText, ...calcCompareStats(values) }
      // 传入当前材质规格，使每个分组使用各自的最低价数据
      if (lowPriceCtx) applyMaterialDetailLowPriceMin(line, m, lowPriceCtx, supplierKeys, spec)
      lines.push(line)
    }
    if (lines.length) groups.push({ title: spec || '材料', lines })
  }
  return groups
}

/** 加工成本展开：按工站分组；仅展示各供应商「加工费」；平均价/制程最低价只在主表「加工成本」行展示 */
const buildProcessDetailGroups = (
  quotes: any[],
  supplierKeys: string[],
  metrics: ComparisonDetailMetric[] = COMPARE_PRICE_PROCESS_DETAIL_METRICS,
  stationNameByCode?: Record<string, string>
): ComparisonDetailGroup[] => {
  const stations = new Set<string>()
  quotes.forEach((q) => {
    ;(q.process_costs || []).forEach((r: any) => {
      stations.add(String(r.process_station || '').trim() || '工站')
    })
  })
  const sorted = [...stations].sort()
  const groups: ComparisonDetailGroup[] = []
  for (const station of sorted) {
    const lines: ComparisonDetailRow[] = []
    for (const m of metrics) {
      if (shouldSkipProcessDetailMetric(m.fieldKey)) continue
      const values: Record<string, any> = {}
      supplierKeys.forEach((sup, idx) => {
        const raw = findProcessRowByStation(quotes[idx], station)
        const merged = mergeOptionJsonIntoRow(raw || {})
        values[sup] = formatMetricCell(m.get(merged), m.isText, m.label)
      })
      const allDash = supplierKeys.every((s) => values[s] === '-')
      if (allDash) continue
      const line: ComparisonDetailRow = { label: m.label, values, isText: m.isText }
      lines.push(line)
    }
    if (lines.length) {
      groups.push({ title: processStationGroupTitle(station, stationNameByCode), lines })
    }
  }
  return groups
}

/** 其它成本：包装费、运输费；与报价单 `other_costs` 一致，多行按供应商汇总 */
const OTHER_COST_DETAIL_ROWS: Array<{ label: string; field: 'packaging_cost' | 'transportation_cost' }> = [
  { label: '包装费', field: 'packaging_cost' },
  { label: '运输费', field: 'transportation_cost' }
]

const buildOtherCostDetails = (quotes: any[], supplierKeys: string[]): ComparisonDetailRow[] => {
  const lines: ComparisonDetailRow[] = []
  for (const { label, field } of OTHER_COST_DETAIL_ROWS) {
    const values: Record<string, any> = {}
    supplierKeys.forEach((sup, idx) => {
      let sum = 0
      let ok = false
      for (const r of quotes[idx].other_costs || []) {
        const raw = r[field]
        if (raw !== undefined && raw !== null && raw !== '') {
          const n = Number(raw)
          if (Number.isFinite(n)) {
            sum += n
            ok = true
          }
        }
      }
      values[sup] = ok ? sum : '-'
    })
    const allDash = supplierKeys.every((sup) => values[sup] === '-')
    if (!allDash) {
      lines.push({ label, values, ...calcCompareStats(values) })
    }
  }
  return lines
}

const buildComparisonRowsFromPisQuotes = (
  quotes: any[],
  detailOpts?: {
    materialMetrics?: ComparisonDetailMetric[]
    processMetrics?: ComparisonDetailMetric[]
    lowPriceCtx?: LowPriceMinContext | null
    /** 加工工站代码 → 名称，用于展开表分组标题 */
    stationNameByCode?: Record<string, string>
    /** 与询价单头部「税率」一致（如 `firstNonEmptyString` 结果），用于税金行制程最低价 */
    taxRateForProcessMin?: string
  }
) => {
  const supplierKeys = quotes.map((q, idx) => quotationSupplierKey(q, idx))
  const rows: ComparisonRow[] = []

  const pushRow = (key: string, label: string, getter: (q: any) => number | null | undefined) => {
    const values: Record<string, any> = {}
    supplierKeys.forEach((name, idx) => {
      const v = getter(quotes[idx])
      values[name] = v != null && Number.isFinite(Number(v)) ? Number(v) : v ?? '-'
    })
    rows.push({ key, label, values, ...calcCompareStats(values) })
  }

  pushRow('material', '材料成本', (q) => sumMaterialCost(q))
  pushRow('process', '加工成本', (q) => sumProcessCost(q))
  pushRow('other', '其它成本', (q) => sumOtherCost(q))
  // pushRow('overhead', '管销研费用', (q) => sumRfqField(q, 'total_opex_amt'))

  const profitValues: Record<string, any> = {}
  supplierKeys.forEach((name, idx) => {
    profitValues[name] = firstRfqField(quotes[idx], 'profit_rate') ?? '-'
  })
  rows.push({ key: 'profit', label: '利润', values: profitValues, ...calcCompareStats(profitValues) })

  const taxValues: Record<string, any> = {}
  supplierKeys.forEach((name, idx) => {
    const q = quotes[idx]
    const fromItem = firstRfqField(q, 'tax_rate')
    const fromProfit = (q.profit_costs || [])[0]?.tax_rate
    taxValues[name] = fromItem ?? fromProfit ?? '-'
  })
  rows.push({ key: 'tax', label: '税金', values: taxValues, ...calcCompareStats(taxValues) })

  const totalValues: Record<string, any> = {}
  supplierKeys.forEach((name, idx) => {
    const q = quotes[idx]
    const a = q.quote_amount
    if (a !== undefined && a !== null && a !== '') {
      const n = Number(a)
      totalValues[name] = Number.isFinite(n) ? n : a
    } else {
      const s = sumRfqField(q, 'total_price_incl_tax')
      totalValues[name] = s != null ? s : '-'
    }
  })
  rows.push({ key: 'total', label: '总价', values: totalValues, ...calcCompareStats(totalValues) })

  const rankValues = buildRanksByTotal(quotes, supplierKeys)
  rows.push({ key: 'rank', label: '报价排名', values: rankValues })

  /* 议价价格仅由杂采议价记录表回显（比价页加载时 merge），勿用报价明细 winning_bid_price 以免与议价记录不一致 */
  const bargainValues: Record<string, any> = {}
  supplierKeys.forEach((name) => {
    bargainValues[name] = ''
  })
  rows.push({
    key: 'bargain',
    label: '议价价格',
    values: bargainValues,
    avg: undefined,
    min: undefined
  })

  const winValues: Record<string, any> = {}
  supplierKeys.forEach((name, idx) => {
    const flag = quotes[idx]?.is_awarded ?? quotes[idx]?.isAwarded
    winValues[name] = flag === 1 || flag === true ? '是' : '否'
  })
  rows.push({ key: 'award', label: '中标否', values: winValues })

  const lp = detailOpts?.lowPriceCtx ?? null
  const materialGroups = buildMaterialDetailGroups(quotes, supplierKeys, detailOpts?.materialMetrics, lp)
  const processGroups = buildProcessDetailGroups(
    quotes,
    supplierKeys,
    detailOpts?.processMetrics,
    detailOpts?.stationNameByCode
  )
  const otherDetails = buildOtherCostDetails(quotes, supplierKeys)

  const matRow = rows.find((r) => r.key === 'material')
  if (matRow && materialGroups.length) matRow.detailGroups = materialGroups
  // 材料成本行的制程最低价是所有材质分组材料费用的总和
  if (matRow && lp?.totalMaterialProduct != null) {
    matRow.min = lp.totalMaterialProduct
    matRow.minLink = buildMaterialCostMinLink(lp, quotes, {
      materialRowValues: matRow.values,
      supplierKeys
    })
  }
  const procRow = rows.find((r) => r.key === 'process')
  if (procRow && processGroups.length) procRow.detailGroups = processGroups
  const otherRow = rows.find((r) => r.key === 'other')
  if (otherRow && otherDetails.length) {
    otherRow.detailGroups = [{ title: '其它成本明细', lines: otherDetails }]
  }

  const nearlyEqMin = (a: number, b: number) => Math.abs(a - b) < 1e-6
  /** 主表「加工成本」制程最低价（兜底）：列最小值对应报价单，可点击跳转 */
  const setRowMinLinkToLowestQuotation = (
    row: ComparisonRow | undefined,
    sumForQuote: (q: any) => number | null
  ) => {
    if (!row) return
    const targetMin = row.min
    if (
      !allCompareSupplierValuesEqual(row.values, supplierKeys) &&
      typeof targetMin === 'number' &&
      Number.isFinite(targetMin)
    ) {
      for (let i = 0; i < quotes.length; i++) {
        const v = sumForQuote(quotes[i])
        if (v != null && Number.isFinite(v) && nearlyEqMin(v, targetMin)) {
          const id = quotes[i].autoid ?? quotes[i].id
          if (id != null && id !== '') {
            row.minLink = { kind: 'quotation', id }
          }
          break
        }
      }
    } else {
      row.minLink = null
    }
  }
  // 加工成本：与 computeLowPriceMinContext 一致，制程最低价列可链向对应报价单（含各列数值全相等时取最早单）
  const procQid = lp?.minProcessQuotationId
  if (
    procRow &&
    procQid != null &&
    procQid !== '' &&
    typeof lp?.minProcessTotal === 'number' &&
    Number.isFinite(lp.minProcessTotal)
  ) {
    procRow.min = lp.minProcessTotal
    procRow.minLink = { kind: 'quotation', id: procQid }
  } else {
    setRowMinLinkToLowestQuotation(procRow, sumProcessCost)
  }
  if (otherRow) otherRow.minLink = null

  const profitRateRaws = quotes.map((q) => profitCostRowForQuote(q)?.profit_rate)
  const profitMinComputed = computeProfitProcessMinPrice(
    matRow?.min,
    procRow?.min,
    otherRow?.min,
    profitRateRaws
  )

  const profitRow = rows.find((r) => r.key === 'profit')
  if (profitRow) {
    profitRow.min = profitMinComputed
    const pm = formatMinProfitMarginForCompare(profitRateRaws)
    if (pm) profitRow.profitMinMarginDisplay = pm
    const marginMap: Record<string, string> = {}
    supplierKeys.forEach((name, idx) => {
      const pc = profitCostRowForQuote(quotes[idx])
      const s = formatQuotationProfitMarginForCompare(pc?.profit_rate)
      if (s) marginMap[name] = s
    })
    profitRow.profitMarginPctBySupplier = marginMap
  }

  const matAvg = matRow?.avg
  const procAvg = procRow?.avg
  const otherAvg = otherRow?.avg
  const profitAvgComputed = computeProfitRowAveragePrice(matAvg, procAvg, otherAvg, profitRateRaws)
  if (profitRow) {
    profitRow.avg = profitAvgComputed
  }

  const taxRow = rows.find((r) => r.key === 'tax')
  if (taxRow) {
    const tr = String(detailOpts?.taxRateForProcessMin ?? '').trim()
    taxRow.min = computeTaxProcessMinPrice(
      matRow?.min,
      procRow?.min,
      otherRow?.min,
      profitMinComputed,
      tr
    )
    taxRow.avg = computeTaxRowAveragePrice(matAvg, procAvg, otherAvg, profitAvgComputed, tr)
  }

  for (const key of ['material', 'process', 'other', 'profit', 'tax'] as const) {
    const r = rows.find((x) => x.key === key)
    if (r) {
      r.avg = coalesceCompareNumeric(r.avg)
      r.min = coalesceCompareNumeric(r.min)
    }
  }

  const totalRow = rows.find((r) => r.key === 'total')
  if (totalRow) {
    totalRow.min = sumComparisonProcessMinTotals(
      matRow?.min,
      procRow?.min,
      otherRow?.min,
      profitRow?.min,
      taxRow?.min
    )
    totalRow.avg = sumComparisonAverageTotals(
      matRow?.avg,
      procRow?.avg,
      otherRow?.avg,
      profitRow?.avg,
      taxRow?.avg
    )
    totalRow.min = coalesceCompareNumeric(totalRow.min)
    totalRow.avg = coalesceCompareNumeric(totalRow.avg)
  }

  const suppliers = supplierKeys.map((name, idx) => ({
    name: name || `供应商${idx + 1}`,
    code: quotes[idx]?.supplier_code || quotes[idx]?.supplierCode || '',
    quotationId: quotes[idx]?.autoid ?? quotes[idx]?.id
  }))

  return { suppliers, rows }
}

/** 税率等：取首个非空值（接口 tax_rate / 嵌套 rfq_items、profit_costs） */
const firstNonEmptyString = (...vals: unknown[]) => {
  for (const v of vals) {
    if (v === null || v === undefined || v === '') continue
    const s = String(v).trim()
    if (s !== '') {
      const num = Number(s)
      if (isNaN(num)) {
        return s
      }
      return `${num.toFixed(COMPARE_DECIMAL_PLACES)}%`
    }
  }
  return ''
}

const loadComparisonPage = async (row: any) => {
  comparisonDialog.currentRow = row
  expandedRowKeys.value = []
  comparisonDialog.loading = true
  const rfqFromRow = Array.isArray(row.rfq_items) ? row.rfq_items[0] : undefined
  const profitFromRow = Array.isArray(row.profit_costs)
    ? rfqFromRow?.part_id
      ? row.profit_costs.find((p: any) => p.part_id === rfqFromRow.part_id) || row.profit_costs[0]
      : row.profit_costs[0]
    : undefined
  comparisonDialog.baseInfo = {
    code: row.inquiry_no || '',
    partNo: String(row.part_no || row.part_id || rfqFromRow?.part_id || '').trim(),
    partName: String(row.part_name || rfqFromRow?.product_name || '').trim(),
    targetPrice: row.target_price != null ? String(row.target_price) : '',
    currency: String(row.currency || row.transaction_currency || '').trim(),
    taxRate: firstNonEmptyString(row.tax_rate, rfqFromRow?.tax_rate, profitFromRow?.tax_rate),
    dealPrice: row.win_price != null ? String(row.win_price) : '-',
    lowestProcessPrice: '-'
  }
  try {
    const listRes = await getQuotationList({ inquiry_no: row.inquiry_no, page: 1, page_size: 200 })
    const list = extractQuotationList(listRes)
    const details = await Promise.all(
      list.map((q: any) => getQuotationDetail(q.autoid ?? q.id))
    )
    const quotes = details.map((r: any) => unwrapQuotationDetail(r)).filter(Boolean)
    /** 杂采材料：按材质聚合最低单价（与报价 material_spec 对齐），禁止跨材质取全局最低 */
    const miscMinBySpec: Record<string, { price: number; factory?: string }> = {}
    try {
      const mres = await GetMaterials({ page: 1, page_size: 5000 })
      const mlist = extractQuotationList(mres)
      for (const it of mlist) {
        if (it.status != null && Number(it.status) !== 1) continue
        const p = Number(it.price)
        if (!Number.isFinite(p)) continue
        const matRaw = it.materialtype ?? it.material_type ?? it.material
        const mat = String(matRaw ?? '')
          .trim()
          .replace(/\s+/g, ' ')
        if (!mat) continue
        const fac = String(it.factory ?? it.company_code ?? '').trim()
        const prev = miscMinBySpec[mat]
        if (!prev || p < prev.price) {
          miscMinBySpec[mat] = { price: p, factory: fac || undefined }
        }
      }
    } catch {
      /* 杂采材料信息不可用则制程最低价单价仅来自报价 */
    }
    const stationNameByCode = await fetchStationCodeToNameMap()
    const lowPriceCtx = computeLowPriceMinContext(quotes, miscMinBySpec)
    const rq0 = quotes[0]?.rfq_items?.[0]
    if (rq0) {
      if (!comparisonDialog.baseInfo.partNo) comparisonDialog.baseInfo.partNo = String(rq0.part_id || '').trim()
      if (!comparisonDialog.baseInfo.partName) comparisonDialog.baseInfo.partName = String(rq0.product_name || '').trim()
    }
    if (!comparisonDialog.baseInfo.taxRate) {
      const pcQ =
        quotes[0] && Array.isArray(quotes[0].profit_costs)
          ? rq0?.part_id
            ? quotes[0].profit_costs.find((p: any) => p.part_id === rq0.part_id) || quotes[0].profit_costs[0]
            : quotes[0].profit_costs[0]
          : undefined
      comparisonDialog.baseInfo.taxRate = firstNonEmptyString(rq0?.tax_rate, pcQ?.tax_rate)
    }
    if (!comparisonDialog.baseInfo.currency && quotes[0]) {
      const c = quotes[0].currency ?? quotes[0].transaction_currency
      if (c != null && c !== '') comparisonDialog.baseInfo.currency = String(c).trim()
    }
    const { suppliers, rows } = buildComparisonRowsFromPisQuotes(quotes, {
      materialMetrics: COMPARE_PRICE_MATERIAL_DETAIL_METRICS,
      processMetrics: COMPARE_PRICE_PROCESS_DETAIL_METRICS,
      lowPriceCtx,
      stationNameByCode,
      taxRateForProcessMin: comparisonDialog.baseInfo.taxRate
    })
    comparisonDialog.quotes = quotes
    comparisonDialog.suppliers = suppliers
    comparisonDialog.rows = rows
    try {
      const negRes = await api.GetNegotiationRecordsObj(row.id, {})
      const raw = negRes?.data?.data ?? negRes?.data
      const negList = Array.isArray(raw) ? raw : []
      mergeNegotiationIntoComparisonRows(rows, quotes, negList)
      if (negList.length) await applyComparisonRowsAfterNegotiationMerge(rows)
    } catch {
      /* 无议价记录时沿用报价单展示 */
    }
    /** 与表格「制程最低价」列一致：取「总价」行各供应商报价中的最小值，勿用「加工成本」或「议价价格」行 */
    const totalRow = rows.find((r) => r.key === 'total')
    if (totalRow && totalRow.min !== undefined) {
      comparisonDialog.baseInfo.lowestProcessPrice = String(totalRow.min)
    }
  } catch (e: any) {
    comparisonDialog.quotes = []
    comparisonDialog.suppliers = []
    comparisonDialog.rows = []
    ElMessage.error(e?.message || '加载比价信息失败')
  } finally {
    comparisonDialog.loading = false
  }
}

/** 免登录分享：后端已组装 inquiry / quotations / materials / stations / negotiation_records */
const loadComparisonFromBundle = async (bundle: {
  inquiry: any
  quotations?: any[]
  materials?: any[]
  stations?: any[]
  negotiation_records?: any[]
}) => {
  const row = bundle.inquiry
  comparisonDialog.currentRow = row
  expandedRowKeys.value = []
  comparisonDialog.loading = true
  const rfqFromRow = Array.isArray(row.rfq_items) ? row.rfq_items[0] : undefined
  const profitFromRow = Array.isArray(row.profit_costs)
    ? rfqFromRow?.part_id
      ? row.profit_costs.find((p: any) => p.part_id === rfqFromRow.part_id) || row.profit_costs[0]
      : row.profit_costs[0]
    : undefined
  comparisonDialog.baseInfo = {
    code: row.inquiry_no || '',
    partNo: String(row.part_no || row.part_id || rfqFromRow?.part_id || '').trim(),
    partName: String(row.part_name || rfqFromRow?.product_name || '').trim(),
    targetPrice: row.target_price != null ? String(row.target_price) : '',
    currency: String(row.currency || row.transaction_currency || '').trim(),
    taxRate: firstNonEmptyString(row.tax_rate, rfqFromRow?.tax_rate, profitFromRow?.tax_rate),
    dealPrice: row.win_price != null ? String(row.win_price) : '-',
    lowestProcessPrice: '-'
  }
  try {
    const quotes = (bundle.quotations || []).filter(Boolean)
    const miscMinBySpec: Record<string, { price: number; factory?: string }> = {}
    for (const it of bundle.materials || []) {
      if (it.status != null && Number(it.status) !== 1) continue
      const p = Number(it.price)
      if (!Number.isFinite(p)) continue
      const matRaw = it.materialtype ?? it.material_type ?? it.material
      const mat = String(matRaw ?? '')
        .trim()
        .replace(/\s+/g, ' ')
      if (!mat) continue
      const fac = String(it.factory ?? it.company_code ?? '').trim()
      const prev = miscMinBySpec[mat]
      if (!prev || p < prev.price) {
        miscMinBySpec[mat] = { price: p, factory: fac || undefined }
      }
    }
    const stationNameByCode = buildStationMapFromList(bundle.stations || [])
    const lowPriceCtx = computeLowPriceMinContext(quotes, miscMinBySpec)
    const rq0 = quotes[0]?.rfq_items?.[0]
    if (rq0) {
      if (!comparisonDialog.baseInfo.partNo) comparisonDialog.baseInfo.partNo = String(rq0.part_id || '').trim()
      if (!comparisonDialog.baseInfo.partName) comparisonDialog.baseInfo.partName = String(rq0.product_name || '').trim()
    }
    if (!comparisonDialog.baseInfo.taxRate) {
      const pcQ =
        quotes[0] && Array.isArray(quotes[0].profit_costs)
          ? rq0?.part_id
            ? quotes[0].profit_costs.find((p: any) => p.part_id === rq0.part_id) || quotes[0].profit_costs[0]
            : quotes[0].profit_costs[0]
          : undefined
      comparisonDialog.baseInfo.taxRate = firstNonEmptyString(rq0?.tax_rate, pcQ?.tax_rate)
    }
    if (!comparisonDialog.baseInfo.currency && quotes[0]) {
      const c = quotes[0].currency ?? quotes[0].transaction_currency
      if (c != null && c !== '') comparisonDialog.baseInfo.currency = String(c).trim()
    }
    const { suppliers, rows } = buildComparisonRowsFromPisQuotes(quotes, {
      materialMetrics: COMPARE_PRICE_MATERIAL_DETAIL_METRICS,
      processMetrics: COMPARE_PRICE_PROCESS_DETAIL_METRICS,
      lowPriceCtx,
      stationNameByCode,
      taxRateForProcessMin: comparisonDialog.baseInfo.taxRate
    })
    comparisonDialog.quotes = quotes
    comparisonDialog.suppliers = suppliers
    comparisonDialog.rows = rows
    const negList = Array.isArray(bundle.negotiation_records) ? bundle.negotiation_records : []
    mergeNegotiationIntoComparisonRows(rows, quotes, negList)
    if (negList.length) await applyComparisonRowsAfterNegotiationMerge(rows)
    const totalRow = rows.find((r) => r.key === 'total')
    if (totalRow && totalRow.min !== undefined) {
      comparisonDialog.baseInfo.lowestProcessPrice = String(totalRow.min)
    }
  } catch (e: any) {
    comparisonDialog.quotes = []
    comparisonDialog.suppliers = []
    comparisonDialog.rows = []
    ElMessage.error(e?.message || '加载比价信息失败')
  } finally {
    comparisonDialog.loading = false
  }
}

const updateComparisonRowStats = (row: any) => {
  if (row?.key === 'bargain') return
  const nums = Object.values(row.values || {})
    .map((v: any) => Number(v))
    .filter((v) => Number.isFinite(v)) as number[]
  if (nums.length) {
    row.avg = nums.reduce((a: number, b: number) => a + b, 0) / nums.length
    row.min = Math.min(...nums)
  } else {
    row.avg = undefined
    row.min = undefined
  }
}

const comparisonRowClassName = ({ row }: any) => {
  const has =
    (row.details && row.details.length) || (row.detailGroups && row.detailGroups.length)
  return has ? '' : 'no-expand'
}

const comparisonRowKeyFn = (row: ComparisonRow) => String(row.key || row.label || '')

const detailHeaderLabel = (row: ComparisonRow) => {
  if (row.key === 'material') return '材质'
  if (row.key === 'process') return '工站'
  if (row.key === 'other') return '类型'
  return '明细'
}

const handleComparisonExpandChange = (row: ComparisonRow, expandedRows: ComparisonRow[]) => {
  expandedRowKeys.value = expandedRows.map((r) => comparisonRowKeyFn(r))
}

const toggleCompareExpand = (row: ComparisonRow) => {
  const has =
    (row.details && row.details.length) || (row.detailGroups && row.detailGroups.length)
  if (!has) return
  const key = comparisonRowKeyFn(row)
  const next = !expandedRowKeys.value.includes(key)
  ;(compareTableRef.value as any)?.toggleRowExpansion?.(row, next)
  if (next) expandedRowKeys.value = [...expandedRowKeys.value, key]
  else expandedRowKeys.value = expandedRowKeys.value.filter((k) => k !== key)
}

const getComparisonRow = (key: string) => comparisonDialog.rows.find((r) => r.key === key)

const stripQuotationForPut = (q: any) => {
  if (!q || typeof q !== 'object') return q
  const { quote_amount, template_sections, inquiry_attachments, ...rest } = q
  return { ...rest }
}

const syncQuotesFromComparisonRows = () => {
  const awardRow = getComparisonRow('award')
  const keys = comparisonDialog.quotes.map((q, idx) => quotationSupplierKey(q, idx))
  return comparisonDialog.quotes.map((quote, idx) => {
    const key = keys[idx]
    const awarded = awardRow?.values?.[key] === '是'
    const next = stripQuotationForPut(quote) as any
    next.is_awarded = awarded ? 1 : 0
    const items = Array.isArray(next.rfq_items)
      ? next.rfq_items.map((it: any) => ({
          ...it,
          is_awarded: awarded ? 1 : 0,
          /* 议价后价格写入杂采议价记录表 bargaining_price，不使用上阶物料「中标价格」 */
          winning_bid_price: null
        }))
      : []
    next.rfq_items = items
    return next
  })
}

const validateComparisonAwardAndBargain = async () => {
  const keys = comparisonDialog.quotes.map((q, idx) => quotationSupplierKey(q, idx))
  const awardRow = getComparisonRow('award')
  const bargainRow = getComparisonRow('bargain')
  const awarded = keys.filter((k) => awardRow?.values?.[k] === '是')
  if (awarded.length === 0) {
    try {
      await ElMessageBox.confirm('当前比价未选择中标供应商，请确定是否流标？', '提示', {
        type: 'warning',
        confirmButtonText: '确定',
        cancelButtonText: '取消'
      })
    } catch {
      return false
    }
    return true
  }
  const missingBargain = awarded.some((k) => {
    const v = bargainRow?.values?.[k]
    if (v === undefined || v === null || v === '') return true
    const n = Number(v)
    return !Number.isFinite(n)
  })
  if (missingBargain) {
    ElMessage.warning('请先为中标供应商维护有效议价价格（数字）后再确认')
    return false
  }
  return true
}

const saveComparison = async (target: 'draft' | 'negotiated' | 'audit') => {
  const st = Number(comparisonDialog.currentRow?.status)
  if (target === 'negotiated' && ![5, 6].includes(st)) {
    ElMessage.warning('仅比议价中状态可确认比价')
    return
  }
  if (target === 'audit' && st !== 7) {
    ElMessage.warning('仅价格审核状态可提交核价')
    return
  }
  if (target !== 'draft' && !(await validateComparisonAwardAndBargain())) return

  const updates = syncQuotesFromComparisonRows()
  if (!updates.length) {
    ElMessage.warning('无可保存的报价数据')
    return
  }
  const keys = comparisonDialog.quotes.map((q, idx) => quotationSupplierKey(q, idx))
  const bargainRow = getComparisonRow('bargain')
  const awardRow = getComparisonRow('award')
  const pickQuotationItemTotals = (quote: any) => {
    const it = (quote.rfq_items || [])[0]
    if (!it) return { total_price_excl_tax: null as number | null, total_price_incl_tax: null as number | null }
    const ex = it.total_price_excl_tax
    const inc = it.total_price_incl_tax
    return {
      total_price_excl_tax: ex != null && ex !== '' && Number.isFinite(Number(ex)) ? Number(ex) : null,
      total_price_incl_tax: inc != null && inc !== '' && Number.isFinite(Number(inc)) ? Number(inc) : null
    }
  }
  const records = comparisonDialog.quotes
    .map((quote, idx) => {
      const key = keys[idx]
      const awarded = awardRow?.values?.[key] === '是'
      const bargRaw = bargainRow?.values?.[key]
      const bargNum = Number(bargRaw)
      const hasBarg = Number.isFinite(bargNum)
      const qn = String(quote.quotation_no || quote.quotationNo || '').trim()
      const totals = pickQuotationItemTotals(quote)
      return {
        quotation_no: qn,
        supplier_code: String(quote.supplier_code || quote.supplierCode || '').trim(),
        is_awarded: awarded ? 1 : 0,
        bargaining_price: hasBarg ? bargNum : null,
        total_price_excl_tax: totals.total_price_excl_tax,
        total_price_incl_tax: totals.total_price_incl_tax
      }
    })
    .filter((r) => r.quotation_no)
  if (!records.length) {
    ElMessage.warning('无可保存的议价记录（缺少报价单号）')
    return
  }

  comparisonDialog.loading = true
  try {
    await api.SaveNegotiationRecordsObj(comparisonDialog.currentRow.id, { records })
    try {
      const negRes = await api.GetNegotiationRecordsObj(comparisonDialog.currentRow.id, {})
      const raw = negRes?.data?.data ?? negRes?.data
      const negList = Array.isArray(raw) ? raw : []
      mergeNegotiationIntoComparisonRows(comparisonDialog.rows, comparisonDialog.quotes, negList)
      if (negList.length) await applyComparisonRowsAfterNegotiationMerge(comparisonDialog.rows)
    } catch {
      /* 回显失败时保留输入框当前值 */
    }
    await Promise.all(
      updates.map((q) => {
        const id = q.autoid ?? q.id
        if (!id) return Promise.resolve()
        return updateQuotation(id, stripQuotationForPut(q))
      })
    )
    if (target === 'negotiated') {
      await api.ConfirmNegotiationObj(comparisonDialog.currentRow.id)
      comparisonDialog.currentRow.status = 7
      ElMessage.success('已确认比价')
      try {
        sessionStorage.setItem('pisadmin_rfq_inquiry_dirty', '1')
      } catch {
        /* ignore */
      }
    } else if (target === 'audit') {
      await api.SubmitPriceAuditObj(comparisonDialog.currentRow.id)
      comparisonDialog.currentRow.status = 8
      ElMessage.success('已提交核价')
      try {
        sessionStorage.setItem('pisadmin_rfq_inquiry_dirty', '1')
      } catch {
        /* ignore */
      }
    } else {
      ElMessage.success('已暂存比价结果')
      try {
        sessionStorage.setItem('pisadmin_rfq_inquiry_dirty', '1')
      } catch {
        /* ignore */
      }
    }
  } catch (e: any) {
    ElMessage.error(formatRfqApiErrorMessage(e, '操作失败'))
  } finally {
    comparisonDialog.loading = false
  }
}

const onSaveComparisonDraft = () => saveComparison('draft')
const onConfirmComparison = () => saveComparison('negotiated')
const onSubmitComparisonReview = () => saveComparison('audit')

const toggleComparisonAward = (row: any, supName: string, val: boolean) => {
  if (!row.values) return
  row.values[supName] = val ? '是' : '否'
}

const loadFromRoute = async () => {
  if (isPublicShare.value) {
    const inquiryId = String((route.query.inquiry_id as string) || '').trim()
    if (!inquiryId) {
      ElMessage.error('缺少 inquiry_id')
      return
    }
    try {
      const res = await api.fetchPublicComparisonBundle({ inquiry_id: inquiryId })
      const body = res?.data as { code?: number; data?: any; msg?: string } | undefined
      if (body && body.code !== undefined && body.code !== 2000) {
        ElMessage.error(body.msg || '加载失败')
        comparisonDialog.quotes = []
        comparisonDialog.suppliers = []
        comparisonDialog.rows = []
        return
      }
      const bundle = body?.data
      if (!bundle?.inquiry) {
        ElMessage.error('数据无效')
        return
      }
      await loadComparisonFromBundle(bundle)
    } catch (e: any) {
      const msg =
        e?.response?.data?.msg ||
        e?.msg ||
        e?.message ||
        '加载比价信息失败'
      ElMessage.error(msg)
      comparisonDialog.quotes = []
      comparisonDialog.suppliers = []
      comparisonDialog.rows = []
    }
    return
  }
  const id = String(route.params.id || '').trim()
  if (!id) {
    ElMessage.error('缺少询价单 ID')
    goBack()
    return
  }
  let row: any
  try {
    const res = await api.GetObj(id)
    row = unwrapInquiryDetail(res)
    if (!row || (row.id == null && row.inquiry_no == null)) {
      ElMessage.error('询价单不存在')
      goBack()
      return
    }
  } catch (e: any) {
    ElMessage.error(e?.message || '加载询价单失败')
    goBack()
    return
  }
  await loadComparisonPage(row)
}

watch(
  () => route.fullPath,
  () => {
    loadFromRoute()
  },
  { immediate: true }
)

</script>

<style scoped>
.compare-price-page {
  box-sizing: border-box;
}
.compare-price-page--public-share {
  height: 100vh !important;
  min-height: 100vh;
  border-radius: 0;
}
.compare-price-page--public-share .compare-price-body {
  padding: 8px 10px 12px;
}
.compare-price-page--public-share :deep(.fs-page-header) {
  display: none;
}
.compare-price-page :deep(.fs-page-header) {
  border-bottom: none;
  padding: 0;
  flex-shrink: 0;
}
.compare-price-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  width: 100%;
  padding: 10px 16px 12px;
  background: linear-gradient(180deg, var(--el-bg-color) 0%, var(--el-fill-color-blank) 100%);
  border-bottom: 1px solid var(--el-border-color-lighter);
}
.compare-price-toolbar__left {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}
.compare-price-back {
  padding: 6px 10px 6px 6px;
  color: var(--el-text-color-regular);
}
.compare-price-back:hover {
  color: var(--el-color-primary);
}
.compare-price-back__icon {
  margin-right: 2px;
  vertical-align: middle;
}
.compare-price-toolbar__title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  letter-spacing: 0.02em;
}
.compare-readonly-cell {
  display: inline-block;
  min-height: 22px;
  line-height: 22px;
  color: var(--el-text-color-primary);
}
.compare-price-body {
  padding: 12px 16px 16px;
  box-sizing: border-box;
  min-height: 0;
}
.compare-price-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 10px;
  padding: 12px 20px 14px;
  width: 100%;
  box-sizing: border-box;
}
.compare-price-page :deep(.fs-page-footer) {
  flex-shrink: 0;
  border-top: 1px solid var(--el-border-color-lighter);
  background: var(--el-bg-color);
  padding: 0;
}

.compare-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.compare-info {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px 12px;
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: #fafafa;
}
.compare-info .info-item {
  display: flex;
  gap: 6px;
  color: #374151;
  font-size: 13px;
}
.compare-info .info-item .label {
  color: #6b7280;
}
.compare-table :deep(.is-min) {
  color: #0ea5e9;
  font-weight: 600;
}
.compare-table :deep(.no-expand .el-table__expand-icon) {
  visibility: hidden;
}
.compare-table :deep(.el-table__expanded-cell) {
  padding: 6px 12px;
  background: #f9fafb;
}
.compare-detail {
  padding: 4px 0 6px;
}
.compare-detail-group {
  margin-bottom: 12px;
}
.compare-detail-group:last-child {
  margin-bottom: 0;
}
.compare-detail-group-title {
  font-weight: 600;
  font-size: 13px;
  color: #065f46;
  background: linear-gradient(90deg, #d1fae5 0%, #ecfdf5 55%, transparent 100%);
  padding: 6px 10px;
  margin-bottom: 6px;
  border-radius: 4px;
  border-left: 3px solid #10b981;
}
.compare-detail-table {
  margin: 0;
}
.no-detail {
  color: #9ca3af;
  padding: 6px 0;
}
.expand-toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  margin-right: 6px;
  cursor: pointer;
  color: #374151;
  user-select: none;
  font-weight: 700;
}
.compare-table :deep(.hidden-expand .el-table__expand-icon) {
  opacity: 0;
  pointer-events: none;
}
.compare-table :deep(.el-table__header .hidden-expand .cell) {
  display: none;
}

.supplier-header-link {
  cursor: pointer;
  color: var(--el-color-primary);
  text-decoration: underline;
  text-underline-offset: 2px;
}
.supplier-header-link:hover {
  opacity: 0.85;
}

.compare-min-link {
  cursor: pointer;
  color: var(--el-color-primary);
  text-decoration: underline;
  text-underline-offset: 2px;
}
.compare-min-link:hover {
  opacity: 0.85;
}

.material-min-split-tooltip {
  line-height: 1.55;
  text-align: left;
}
</style>
