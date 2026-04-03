<template>
  <fs-page class="compare-price-page" v-loading="comparisonDialog.loading">
    <template #header>
      <header class="compare-price-toolbar">
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
          <div class="info-item"><span class="label">目标价格</span><span class="value">{{ displayNumericEmpty(comparisonDialog.baseInfo.targetPrice) }}</span></div>
          <div class="info-item"><span class="label">交易币别</span><span class="value">{{ displayTextEmpty(comparisonDialog.baseInfo.currency) }}</span></div>
          <div class="info-item"><span class="label">税率</span><span class="value">{{ displayPercentRate(comparisonDialog.baseInfo.taxRate) }}</span></div>
          <div class="info-item"><span class="label">当前成交价</span><span class="value">{{ displayNumericEmpty(comparisonDialog.baseInfo.dealPrice) }}</span></div>
          <div class="info-item"><span class="label">制程最低价</span><span class="value">{{ displayNumericEmpty(comparisonDialog.baseInfo.lowestProcessPrice) }}</span></div>
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
            <template #default="{ row }">
              <div class="compare-detail">
                <template v-if="row.detailGroups && row.detailGroups.length">
                  <div v-for="grp in row.detailGroups" :key="grp.title" class="compare-detail-group">
                    <div class="compare-detail-group-title">{{ grp.title }}</div>
                    <el-table :data="grp.lines" size="small" border class="compare-detail-table">
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
                        <template #default="{ row: line }">{{ formatCompareAvg(line.avg, row.key) }}</template>
                      </el-table-column>
                      <el-table-column prop="min" label="制程最低价" width="110">
                        <template #default="{ row: line }">
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
                              {{ formatCompareMin(line.min, row.key) }}
                            </span>
                          </el-tooltip>
                          <span
                            v-else-if="line.minLink?.kind === 'quotation' || line.minLink?.kind === 'misc_materials'"
                            class="compare-min-link"
                            @click.stop="openCompareMinLink(line.minLink)"
                          >
                            {{ formatCompareMin(line.min, row.key) }}
                          </span>
                          <span v-else>{{ formatCompareMin(line.min, row.key) }}</span>
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
                <el-input v-model="row.values[sup.name]" size="small" placeholder="请输入议价价" />
              </template>
              <template v-else-if="row.key === 'award'">
                <el-switch
                  :model-value="row.values[sup.name] === '是'"
                  @update:model-value="(val: boolean) => toggleComparisonAward(row, sup.name, val)"
                  active-text="是"
                  inactive-text="否"
                />
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
              <template v-else-if="row.key === 'material' && row.minLink">
                <el-tooltip
                  v-if="row.minLink.kind === 'material_cost_split'"
                  placement="top"
                  effect="dark"
                >
                  <template #content>
                    <div class="material-min-split-tooltip">
                      <div>
                        最小重量：{{ formatMaterialSplitTooltipNumber(row.minLink.weight) }}（{{ row.minLink.weightSource }}）
                      </div>
                      <div>
                        最小单价：{{ formatMaterialSplitTooltipNumber(row.minLink.unitPrice) }}（{{ row.minLink.unitPriceSource }}）
                      </div>
                    </div>
                  </template>
                  <span class="compare-min-link" @click.stop>{{ formatCompareMin(row.min, row.key) }}</span>
                </el-tooltip>
                <el-tooltip
                  v-else-if="row.minLink.kind === 'misc_materials' && row.minLink.sourceFactory"
                  placement="top"
                  effect="dark"
                >
                  <template #content>
                    <div class="material-min-split-tooltip">最低单价来源厂区：{{ row.minLink.sourceFactory }}</div>
                  </template>
                  <span class="compare-min-link" @click.stop="openCompareMinLink(row.minLink)">
                    {{ formatCompareMin(row.min, row.key) }}
                  </span>
                </el-tooltip>
                <span v-else class="compare-min-link" @click.stop="openCompareMinLink(row.minLink)">
                  {{ formatCompareMin(row.min, row.key) }}
                </span>
              </template>
              <template v-else>{{ formatCompareMin(row.min, row.key) }}</template>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <template #footer>
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
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getList as getQuotationList,
  getDetail as getQuotationDetail,
  update as updateQuotation
} from '../../../pissupplier/quotation/api'
import {
  formatRfqApiErrorMessage,
  displayNumericEmpty,
  displayTextEmpty,
  displayPercentRate,
  buildMaterialComparisonMetricsFromTemplateFields,
  buildProcessComparisonMetricsFromTemplateFields,
  shouldSkipMaterialDetailMetric,
  shouldSkipProcessDetailMetric,
  computeLowPriceMinContext,
  applyMaterialDetailLowPriceMin,
  applyProcessDetailLowPriceMin,
  buildMaterialCostMinLink,
  type CompareMinLink,
  type ComparisonDetailMetric,
  type LowPriceMinContext
} from './crud'
import * as api from './api'
import * as costTemplateApi from '../cost_template/api'
import { GetList as GetMaterials } from '../misc_materials/api'

const route = useRoute()
const router = useRouter()

const unwrapInquiryDetail = (res: any) => res?.data?.data ?? res?.data ?? res

const goBack = () => {
  router.back()
}

/** 比价页：按模板编号拉取成本结构（与询价详情页共用逻辑） */
const templates = ref<any[]>([])
const templateLoading = ref(false)
const templatesLoaded = ref(false)

const normalizeSections = (sections: any) => {
  if (typeof sections === 'string') {
    try {
      const parsed = JSON.parse(sections)
      return Array.isArray(parsed) ? parsed : []
    } catch (e) {
      console.warn('模版 sections 解析失败', e)
      return []
    }
  }
  return Array.isArray(sections) ? sections : []
}

const hasTemplateSections = (tpl: any) => {
  const sections = normalizeSections(tpl?.sections)
  return Array.isArray(sections) && sections.length > 0
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

const normalizeSupplierRequiredCodeField = (r: any) => {
  const raw = r?.supplier_required ?? r?.supplierRequiredCode ?? r?.supplier_behavior ?? r?.supplierBehavior
  const code = Number(raw)
  if (Number.isInteger(code) && code >= 0 && code <= 6) return code
  return 0
}

const buildSectionsFromCostTemplate = (head: any) => {
  const items = Array.isArray(head?.items) ? head.items : []
  if (!items.length) return []
  const group = new Map<string, any[]>()
  items.forEach((it: any) => {
    const cat = String(it.cost_category ?? '')
    const title = costCategoryToTitle[cat] || '其它成本'
    if (!group.has(title)) group.set(title, [])
    group.get(title)!.push(it)
  })
  const order = ['产品明细', '材料成本', '加工成本', '其它成本', '管销研费用', '利润', '税金']
  return order
    .filter((t) => group.has(t))
    .map((title) => {
      const rows = (group.get(title) || []).slice().sort((a: any, b: any) => (a.item_order || 0) - (b.item_order || 0))
      return {
        id: title,
        title,
        enabled: true,
        fields: rows.map((r: any) => ({
          key: r.item_no || '',
          label: r.item_name_cn || r.item_no || '',
          autoFill: Number(r.is_computed || 0) === 1,
          purchaserRequired: Number(r.purchaser_required || 0) === 1,
          supplierRequiredCode: normalizeSupplierRequiredCodeField(r)
        }))
      }
    })
}

const fetchTemplateDetailIfNeeded = async (tpl: any) => {
  if (!tpl) return tpl
  if (hasTemplateSections(tpl)) return tpl
  if (!tpl?.id) return tpl
  try {
    const res = await costTemplateApi.GetObj(tpl.id)
    const head = res?.data?.data || res?.data || res
    if (head && typeof head === 'object') {
      const sections = buildSectionsFromCostTemplate(head)
      const merged = { ...tpl, ...head, sections }
      const idx = templates.value.findIndex((t: any) => t.id === tpl.id)
      if (idx >= 0) templates.value[idx] = merged
      return merged
    }
  } catch (e) {
    console.warn('加载成本结构模板详情失败', e)
  }
  return tpl
}

const fetchTemplates = async () => {
  templateLoading.value = true
  try {
    const res = await costTemplateApi.GetList({
      procurement_category: '2',
      acti: 'Y',
      status: 1,
      page: 1,
      pageSize: 200,
      page_size: 200
    } as Record<string, unknown>)
    const list =
      res?.data?.results ||
      res?.data?.data ||
      res?.data?.list ||
      res?.results ||
      res?.list ||
      res?.data ||
      []
    templates.value = Array.isArray(list) ? list : []
    templatesLoaded.value = true
  } catch (e) {
    console.warn('加载询价模版失败', e)
    templates.value = []
    templatesLoaded.value = true
  } finally {
    templateLoading.value = false
  }
}

const ensureTemplatesLoaded = async () => {
  if (!templatesLoaded.value) {
    await fetchTemplates()
  }
}

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

/** 打开报价单详情路由页（默认查看模式，与供应商端详情页一致） */
const openQuotationPreview = (supplierIndex: number) => {
  const quote: any = comparisonDialog.quotes[supplierIndex]
  const sup = comparisonDialog.suppliers[supplierIndex]
  const id = sup?.quotationId ?? quote?.autoid ?? quote?.id
  if (id == null || id === '') {
    ElMessage.warning('暂无该供应商报价单数据')
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
    router.push({
      name: 'PissupplierQuotationDetail',
      params: { id: String(link.id) }
    })
  } else {
    router.push({ name: 'PisadminMiscMaterialsIndex' })
  }
}

const comparisonInquiryStatus = computed(() => Number(comparisonDialog.currentRow?.status))

/** 比价主表：利润/税金行为金额合计，与材料成本等同用两位小数，不加 %（仅表头「税率」用 displayPercentRate） */
const formatComparisonMainCell = (row: ComparisonRow, v: unknown) => {
  if (row.key === 'rank') {
    if (v === null || v === undefined || v === '') return '-'
    return String(v)
  }
  if (v === null || v === undefined || v === '' || v === '-') return '0.00'
  const n = Number(v)
  if (Number.isFinite(n)) return n.toFixed(2)
  return String(v)
}

const formatCompareAvg = (v: unknown, _rowKey?: string) => {
  if (v === undefined || v === null) return '0.00'
  const n = Number(v)
  if (Number.isFinite(n)) return n.toFixed(2)
  return String(v)
}

const formatCompareMin = (v: unknown, _rowKey?: string) => {
  if (v === undefined || v === null) return '0.00'
  const n = Number(v)
  if (Number.isFinite(n)) return n.toFixed(2)
  return String(v)
}

/** 材料成本分项浮窗：与制程最低价列数字格式一致 */
const formatMaterialSplitTooltipNumber = (v: number) => {
  if (!Number.isFinite(v)) return '—'
  return v.toFixed(2)
}

const extractQuotationList = (res: any): any[] => {
  const raw = res?.data?.results ?? res?.data?.data?.results ?? res?.data?.list ?? res?.data
  return Array.isArray(raw) ? raw : []
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

/** 比价展开明细：按行标签区分数值(空→0.00)与文本(空→-) */
const formatMetricDetailCell = (v: unknown, label: string, isText?: boolean) => {
  if (isText === true || label === '备注') return displayTextEmpty(v)
  return displayNumericEmpty(v)
}

const formatMetricCell = (v: unknown, isText: boolean) => {
  return isText ? displayTextEmpty(v) : displayNumericEmpty(v)
}

const findMaterialRowBySpec = (q: any, spec: string) => {
  const t = String(spec || '').trim()
  return (q.material_costs || []).find((r: any) => String(r.material_spec || '').trim() === t)
}

const findProcessRowByStation = (q: any, station: string) => {
  const t = String(station || '').trim()
  return (q.process_costs || []).find((r: any) => String(r.process_station || '').trim() === t)
}

/** 无模板或模板无字段时的回退顺序（与旧版硬编码一致） */
const DEFAULT_MATERIAL_COMPARISON_METRICS: ComparisonDetailMetric[] = [
  { label: '用量(重量)', get: (r) => r?.weight, isText: false },
  { label: '长', get: (r) => r?.length, isText: false },
  { label: '宽', get: (r) => r?.width, isText: false },
  { label: '高', get: (r) => r?.height, isText: false },
  { label: '材料单价', get: (r) => r?.unit_price, isText: false },
  { label: '比重', get: (r) => r?.specific_gravity, isText: false },
  { label: '数量', get: (r) => r?.qty, isText: false },
  { label: '材料费用', get: (r) => r?.material_cost, isText: false },
  { label: '备注', get: (r) => r?.remark, isText: true }
]

const DEFAULT_PROCESS_COMPARISON_METRICS: ComparisonDetailMetric[] = [
  { label: '加工计量', get: (r) => r?.process_qty, isText: false },
  { label: '单位', get: (r) => r?.unit, isText: true },
  { label: '费率', get: (r) => r?.unit_rate, isText: false },
  { label: '加工时间', get: (r) => r?.process_time ?? r?.processTime, isText: false },
  { label: '加工费用', get: (r) => r?.process_price, isText: false },
  { label: '备注', get: (r) => r?.remark, isText: true }
]

/** 材料成本展开：按材料规格分组；「制程最低价」列对重量/单价/材料费用行使用全局口径（与后端落库一致） */
const buildMaterialDetailGroups = (
  quotes: any[],
  supplierKeys: string[],
  metrics: ComparisonDetailMetric[] = DEFAULT_MATERIAL_COMPARISON_METRICS,
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
        values[sup] = formatMetricCell(m.get(merged), m.isText)
      })
      const allDash = supplierKeys.every((sup) => values[sup] === '-')
      if (allDash) continue
      const line: ComparisonDetailRow = { label: m.label, values, isText: m.isText, ...calcCompareStats(values) }
      if (lowPriceCtx) applyMaterialDetailLowPriceMin(line, m, lowPriceCtx, supplierKeys)
      lines.push(line)
    }
    if (lines.length) groups.push({ title: spec || '材料', lines })
  }
  return groups
}

/** 加工成本展开：按工站分组；「加工费用」行制程最低价为各报价单加工费合计之最小值 */
const buildProcessDetailGroups = (
  quotes: any[],
  supplierKeys: string[],
  metrics: ComparisonDetailMetric[] = DEFAULT_PROCESS_COMPARISON_METRICS,
  lowPriceCtx: LowPriceMinContext | null = null
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
        values[sup] = formatMetricCell(m.get(merged), m.isText)
      })
      const allDash = supplierKeys.every((s) => values[s] === '-')
      if (allDash) continue
      const line: ComparisonDetailRow = { label: m.label, values, isText: m.isText, ...calcCompareStats(values) }
      if (lowPriceCtx) applyProcessDetailLowPriceMin(line, m, lowPriceCtx)
      lines.push(line)
    }
    if (lines.length) groups.push({ title: station || '工站', lines })
  }
  return groups
}

/** 其它成本：包装费 / 运输费（保持原单层表） */
const buildOtherCostDetails = (quotes: any[], supplierKeys: string[]): ComparisonDetailRow[] => {
  const map = new Map<string, ComparisonDetailRow>()
  quotes.forEach((q, idx) => {
    const sup = supplierKeys[idx]
    for (const r of q.other_costs || []) {
      const pkg = r.packaging_cost
      const tr = r.transportation_cost
      if (pkg !== undefined && pkg !== null && pkg !== '') {
        const label = '包装费'
        if (!map.has(label)) map.set(label, { label, values: {} })
        const n = Number(pkg)
        map.get(label)!.values[sup] = Number.isFinite(n) ? n : pkg
      }
      if (tr !== undefined && tr !== null && tr !== '') {
        const label = '运输费'
        if (!map.has(label)) map.set(label, { label, values: {} })
        const n = Number(tr)
        map.get(label)!.values[sup] = Number.isFinite(n) ? n : tr
      }
    }
  })
  return Array.from(map.values()).map((d) => ({
    ...d,
    ...calcCompareStats(d.values)
  }))
}

const buildComparisonRowsFromPisQuotes = (
  quotes: any[],
  detailOpts?: {
    materialMetrics?: ComparisonDetailMetric[]
    processMetrics?: ComparisonDetailMetric[]
    lowPriceCtx?: LowPriceMinContext | null
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
  pushRow('overhead', '管销研费用', (q) => sumRfqField(q, 'total_opex_amt'))

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
  const processGroups = buildProcessDetailGroups(quotes, supplierKeys, detailOpts?.processMetrics, lp)
  const otherDetails = buildOtherCostDetails(quotes, supplierKeys)

  const matRow = rows.find((r) => r.key === 'material')
  if (matRow && materialGroups.length) matRow.detailGroups = materialGroups
  if (matRow && lp?.materialProduct != null) {
    matRow.min = lp.materialProduct
    matRow.minLink = buildMaterialCostMinLink(lp, quotes, {
      materialRowValues: matRow.values,
      supplierKeys
    })
  }
  const procRow = rows.find((r) => r.key === 'process')
  if (procRow && processGroups.length) procRow.detailGroups = processGroups
  if (procRow && lp?.minProcessTotal != null) procRow.min = lp.minProcessTotal
  const otherRow = rows.find((r) => r.key === 'other')
  if (otherRow && otherDetails.length) otherRow.details = otherDetails

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
      return `${num.toFixed(2)}%`
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
    await ensureTemplatesLoaded()
    const tplCode = String(row?.template_code || row?.template || '').trim()
    let tplResolved: any = null
    if (tplCode) {
      tplResolved = templates.value.find((t: any) => t.template_no === tplCode) ?? null
      if (tplResolved) tplResolved = await fetchTemplateDetailIfNeeded(tplResolved)
    }
    let materialMetrics: ComparisonDetailMetric[] | undefined
    let processMetrics: ComparisonDetailMetric[] | undefined
    if (tplResolved) {
      const secs = normalizeSections(tplResolved.sections)
      const matSec = secs.find((s: any) => (s.title || s.name) === '材料成本')
      const procSec = secs.find((s: any) => (s.title || s.name) === '加工成本')
      if (matSec?.fields?.length) {
        const built = buildMaterialComparisonMetricsFromTemplateFields(matSec.fields)
        if (built.length) materialMetrics = built
      }
      if (procSec?.fields?.length) {
        const built = buildProcessComparisonMetricsFromTemplateFields(procSec.fields)
        if (built.length) processMetrics = built
      }
    }
    let miscMinUnitPrice: number | undefined
    let miscMinFactory: string | undefined
    try {
      const mres = await GetMaterials({ page: 1, page_size: 5000 })
      const mlist = extractQuotationList(mres)
      for (const it of mlist) {
        if (it.status != null && Number(it.status) !== 1) continue
        const p = Number(it.price)
        if (!Number.isFinite(p)) continue
        if (miscMinUnitPrice === undefined || p < miscMinUnitPrice) {
          miscMinUnitPrice = p
          const fac = String(it.factory ?? it.company_code ?? '').trim()
          miscMinFactory = fac || undefined
        }
      }
    } catch {
      /* 杂采材料信息不可用则制程最低价单价仅来自报价 */
    }
    const lowPriceCtx = computeLowPriceMinContext(quotes, miscMinUnitPrice, miscMinFactory)
    const { suppliers, rows } = buildComparisonRowsFromPisQuotes(quotes, {
      materialMetrics,
      processMetrics,
      lowPriceCtx
    })
    comparisonDialog.quotes = quotes
    comparisonDialog.suppliers = suppliers
    comparisonDialog.rows = rows
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
  () => route.params.id,
  () => {
    loadFromRoute()
  },
  { immediate: true }
)

onMounted(() => {
  fetchTemplates()
})
</script>

<style scoped>
.compare-price-page {
  box-sizing: border-box;
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
