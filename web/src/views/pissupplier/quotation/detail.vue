<template>
  <fs-page class="quote-detail-page" v-loading="loading">
    <template #header>
      <header class="quote-detail-toolbar">
        <div class="quote-detail-toolbar__left">
          <el-button text class="quote-detail-back" @click="goBack">
            <el-icon class="quote-detail-back__icon"><ArrowLeft /></el-icon>
            返回
          </el-button>
          <h1 class="quote-detail-toolbar__title">{{ pageTitle }}</h1>
        </div>
        <div class="quote-detail-toolbar__meta">
          <span class="quote-detail-toolbar__meta-label">报价状态</span>
          <el-tag :type="statusTagType(current.status)" effect="light" round>
            {{ statusLabel(current.status) }}
          </el-tag>
        </div>
      </header>
    </template>

    <div class="detail-body">
      <div class="detail-card">
        <el-tabs v-model="activeTab" type="border-card" class="detail-tabs tabs-fill">
          <el-tab-pane label="询价单信息" name="inquiry">
            <div class="tab-pane-body quote-tab-pane">
              <el-descriptions :column="descColumns" border size="small" class="quote-descriptions">
                <el-descriptions-item label="询价单号">{{ displayText(current.inquiryCode) }}</el-descriptions-item>
                <el-descriptions-item label="询价单名称" :span="2">{{ displayText(current.inquiryTitle) }}</el-descriptions-item>
                <el-descriptions-item label="询价模板">{{ displayText(templateLabel(current.template)) }}</el-descriptions-item>
                <el-descriptions-item label="交易币别">{{ displayText(current.currency) }}</el-descriptions-item>
                <el-descriptions-item label="报价截止时间">{{ formatQuoteDeadlineDisplay(current.quoteDeadline) || '—' }}</el-descriptions-item>
                <el-descriptions-item label="交易厂区">{{ displayText(current.companyShortName || current.inquiryCompanyCode) }}</el-descriptions-item>
                <el-descriptions-item label="备注">{{ displayText(current.inquiryRemark) }}</el-descriptions-item>
              </el-descriptions>
              <div class="section-block">
                <div class="section-block__title">询价附件</div>
                <div class="inquiry-attachments">
                  <div v-for="group in inquiryAttachmentGroups" :key="group.fileType" class="inquiry-attachments__block">
                    <div class="inquiry-attachments__type">{{ group.label }}</div>
                    <div class="inquiry-attachments__links">
                      <template v-for="(file, idx) in group.items" :key="`${group.fileType}-${file.id ?? idx}-${file.file_name}`">
                        <el-link
                          v-if="inquiryAttachmentHref(file) !== '#'"
                          type="primary"
                          :href="inquiryAttachmentHref(file)"
                          target="_blank"
                          rel="noopener noreferrer"
                          class="inquiry-attachments__link"
                        >
                          {{ file.file_name || '（未命名）' }}
                        </el-link>
                        <span v-else class="inquiry-attachments__link inquiry-attachments__link--text">
                          {{ file.file_name || '（未命名）' }}
                        </span>
                      </template>
                    </div>
                  </div>
                  <div v-if="!inquiryAttachmentGroups.length" class="inquiry-attachments__empty">暂无询价附件</div>
                </div>
              </div>
            </div>
          </el-tab-pane>

        <el-tab-pane label="报价基础信息" name="base">
          <div class="tab-pane-body quote-tab-pane">
            <template v-if="isReadOnly">
              <el-descriptions :column="descColumns" border size="small" class="quote-descriptions">
                <el-descriptions-item label="联系人">{{ displayText(current.base.contact) }}</el-descriptions-item>
                <el-descriptions-item label="联系电话">{{ displayText(current.base.phone) }}</el-descriptions-item>
                <el-descriptions-item label="联系邮箱">{{ displayText(current.base.email) }}</el-descriptions-item>
                <el-descriptions-item label="报价有效期(天)">{{ displayText(current.base.validityDays) }}</el-descriptions-item>
                <el-descriptions-item label="交货周期(天)">{{ displayText(current.base.leadTimeDays) }}</el-descriptions-item>
                <el-descriptions-item label="付款方式">{{ formatPaymentTermLabel(current.base.paymentTerm) }}</el-descriptions-item>
              </el-descriptions>
            </template>
            <el-form v-else :model="current.base" label-width="108px" class="grid-form grid-form--edit">
              <el-form-item label="联系人">
                <el-input v-model="current.base.contact" />
              </el-form-item>
              <el-form-item label="联系电话">
                <el-input v-model="current.base.phone" />
              </el-form-item>
              <el-form-item label="联系邮箱">
                <el-input v-model="current.base.email" />
              </el-form-item>
              <el-form-item label="报价有效期(天)">
                <el-input v-model="current.base.validityDays" type="number" />
              </el-form-item>
              <el-form-item label="交货周期(天)">
                <el-input v-model="current.base.leadTimeDays" type="number" />
              </el-form-item>
              <el-form-item label="付款方式">
                <el-select v-model="current.base.paymentTerm" placeholder="选择付款方式" class="w-full">
                  <el-option label="T/T 30%预付，70%出货前" value="tt_30_70" />
                  <el-option label="月结30天" value="net30" />
                  <el-option label="月结45天" value="net45" />
                  <el-option label="全额预付" value="prepaid" />
                </el-select>
              </el-form-item>
            </el-form>

            <div class="section-block">
              <div class="section-block__title">报价合计</div>
          <div class="quote-summary">
            <el-table
              :data="quoteSummaryRows"
              border
              size="small"
              class="quote-summary__table"
              :row-class-name="quoteSummaryRowClassName"
            >
              <el-table-column prop="section" label="组成" min-width="140" />
              <el-table-column label="金额">
                <template #default="{ row }">
                  {{ formatMoney(row.amount) }}
                </template>
              </el-table-column>
            </el-table>
            <div class="quote-summary__total">
              <div class="quote-summary__label">未税价</div>
              <div class="quote-summary__value quote-summary__value--pretax">{{ formatMoney(quoteAmountPreTax) }}</div>
              <div class="quote-summary__label">最终报价</div>
              <div class="quote-summary__value">{{ formatMoney(quoteTotal) }}</div>
            </div>
          </div>
            </div>

            <div class="section-block">
              <div class="section-block__title">报价附件与说明</div>
              <div v-if="isReadOnly" class="attach-readonly">
                <ul v-if="(current.attachments || []).length" class="attach-readonly__list">
                  <li v-for="(file, idx) in current.attachments" :key="file.uid ?? idx" class="attach-readonly__item">
                    <el-link
                      v-if="quotationAttachmentHref(file) !== '#'"
                      type="primary"
                      :href="quotationAttachmentHref(file)"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {{ file.name || file.file_name || '附件' }}
                    </el-link>
                    <span v-else>{{ file.name || file.file_name || '—' }}</span>
                  </li>
                </ul>
                <p v-else class="attach-readonly__empty">暂无报价附件</p>
                <div class="attach-readonly__remark-wrap">
                  <span class="attach-readonly__remark-label">补充说明</span>
                  <p class="attach-readonly__remark">{{ (current.remark || '').trim() || '—' }}</p>
                </div>
              </div>
              <div v-else class="attach-row">
                <el-upload
                  action="#"
                  :auto-upload="false"
                  multiple
                  list-type="text"
                  drag
                  :file-list="current.attachments"
                  :on-change="onQuotationAttachmentListChange"
                  :on-remove="onQuotationAttachmentListChange"
                >
                  <template #file="{ file }">
                    <div class="quotation-upload-file">
                      <el-link
                        v-if="quotationAttachmentHref(file) !== '#'"
                        type="primary"
                        :href="quotationAttachmentHref(file)"
                        target="_blank"
                        rel="noopener noreferrer"
                        class="quotation-upload-file__link"
                      >
                        {{ file.name }}
                      </el-link>
                      <span v-else class="quotation-upload-file__name">{{ file.name }}</span>
                      <el-button
                        link
                        type="danger"
                        size="small"
                        class="quotation-upload-file__rm"
                        @click="removeQuotationAttachment(file)"
                      >
                        删除
                      </el-button>
                    </div>
                  </template>
                  <i class="el-icon-upload" />
                  <div class="el-upload__text">拖拽或点击上传 (PDF/DOC/JPG/PNG)</div>
                </el-upload>
                <el-input v-model="current.remark" type="textarea" :rows="4" placeholder="补充报价说明" />
              </div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="成本结构" name="cost">
          <div class="tab-pane-body quote-tab-pane">
          <div v-if="!isReadOnly" class="cost-toolbar">
            <el-button size="small" @click="loadCostRowsFromTemplate(current.templateSections, true)">清空已填内容</el-button>
          </div>
          <div class="cost-groups">
            <div v-for="section in primarySections" :key="section" class="cost-group">
              <div class="cost-group-header">
                <div class="cost-section-title">{{ costSectionDisplayTitle(section) }}</div>
                <div class="cost-group-header__tail">
                  <span v-if="costSectionSubtotalLabel(section)" class="cost-section-subtotal">{{
                    costSectionSubtotalLabel(section)
                  }}</span>
                  <el-button
                    size="small"
                    type="primary"
                    @click="addCostRow(section)"
                    v-if="sectionAddConfig[section] && !isReadOnly"
                  >新增一行</el-button>
                </div>
              </div>
              <el-table
                :data="(groupedCostRows[section] || [])"
                border
                size="small"
                :class="['cost-el-table', 'mb12', section === '其它成本' ? 'compact-cost-table' : '']"
              >
                <el-table-column
                  v-for="col in sectionColumns[section] || []"
                  :key="col.key"
                  :prop="col.key"
                  :label="col.label"
                >
                  <template #default="{ row }">
                    <el-select
                      v-if="section === '材料成本' && col.key === 'material'"
                      v-model="row.values[col.key]"
                      placeholder="选择材质"
                      :loading="materialLoading"
                      filterable
                      clearable
                      :disabled="isCostCellDisabled(section, col.key)"
                      @change="(val: string) => handleMaterialSelect(row, val)"
                    >
                      <el-option
                        v-for="m in materialOptions"
                        :key="m.value"
                        :label="m.label"
                        :value="m.value"
                      />
                    </el-select>
                    <el-select
                      v-else-if="section === '加工成本' && (col.key === 'process_station' || col.key === 'processStation')"
                      v-model="row.values[col.key]"
                      placeholder="选择加工工站"
                      :loading="stationLoading"
                      filterable
                      clearable
                      :disabled="isCostCellDisabled(section, col.key)"
                      @change="(val: string) => handleStationSelect(row, val)"
                    >
                      <el-option
                        v-for="s in stationOptions"
                        :key="s.value"
                        :label="s.label"
                        :value="s.value"
                      />
                    </el-select>
                    <el-input
                      v-else-if="section === '加工成本'"
                      v-model="row.values[col.key]"
                      :placeholder="col.label"
                      @input="() => updateProcessCalc(row)"
                      :disabled="isCostCellDisabled(section, col.key)"
                    />
                    <el-input
                      v-else-if="section === '材料成本'"
                      v-model="row.values[col.key]"
                      :placeholder="col.label"
                      @input="() => updateMaterialCalc(row)"
                      :disabled="isCostCellDisabled(section, col.key)"
                    />
                    <el-input
                      v-else
                      v-model="row.values[col.key]"
                      :placeholder="col.label"
                      :disabled="isCostCellDisabled(section, col.key)"
                    />
                  </template>
                </el-table-column>
                <el-table-column v-if="sectionAddConfig[section] && !isReadOnly" label="操作" width="100">
                  <template #default="{ row }">
                    <el-button link type="danger" size="small" @click="removeCostRow(row.id)">移除</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>

            <div class="cost-row-pair">
              <div v-for="section in profitTaxSections" :key="section" class="cost-group">
                <div class="cost-group-header">
                  <div class="cost-section-title">{{ costSectionDisplayTitle(section) }}</div>
                </div>
                <el-table :data="(groupedCostRows[section] || [])" border size="small" class="cost-el-table mb12">
                  <el-table-column
                    v-for="col in sectionColumns[section] || []"
                    :key="col.key"
                    :prop="col.key"
                    :label="col.label"
                  >
                    <template #default="{ row }">
                      <el-input
                        v-model="row.values[col.key]"
                        :placeholder="col.label"
                        :disabled="isCostCellDisabled(section, col.key)"
                      />
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </div>
          </div>

          <div v-if="current.enableCostStructure !== false" class="cost-totals-footer">
            <div class="cost-totals-footer__inner">
              <div class="cost-totals-footer__item">
                <span class="cost-totals-footer__label">成本合计</span>
                <span class="cost-totals-footer__value">{{ formatMoney(quoteRollupForRfq.costSum) }}</span>
              </div>
              <div class="cost-totals-footer__item">
                <span class="cost-totals-footer__label">税前总价合计</span>
                <span class="cost-totals-footer__value">{{ formatMoney(quoteRollupForRfq.preTax) }}</span>
              </div>
              <div class="cost-totals-footer__item">
                <span class="cost-totals-footer__label">税后总价合计</span>
                <span class="cost-totals-footer__value">{{ formatMoney(quoteRollupForRfq.postTax) }}</span>
              </div>
            </div>
          </div>
          </div>
        </el-tab-pane>
      </el-tabs>
      </div>
    </div>

    <template v-if="!isReadOnly && isQuotationEditable(current)" #footer>
      <div class="detail-footer">
        <el-button @click="goBack">取消</el-button>
        <el-button type="primary" @click="saveQuote">保存</el-button>
      </div>
    </template>
  </fs-page>
</template>

<script setup lang="ts">
import { ArrowLeft } from '@element-plus/icons-vue'
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getBaseURL } from '/@/utils/baseUrl'
import {
  useQuoteCrud,
  type InquiryAttachmentRow,
  formatQuoteDeadlineDisplay,
  formatPaymentTermLabel
} from './crud'

const descColumns = 3

/** 成本结构 Tab 各段标题前序号（与业务段名称一致：其它成本） */
const COST_SECTION_DISPLAY_TITLES: Record<string, string> = {
  材料成本: '① 材料成本',
  加工成本: '② 加工成本',
  其它成本: '③ 其它成本',
  利润: '④ 利润',
  税金: '⑤ 税金'
}
function costSectionDisplayTitle(section: string) {
  const raw = String(section ?? '')
    .trim()
    .normalize('NFC')
  const stripped = raw.replace(/^[①②③④⑤⑥⑦⑧⑨⑩]\s*/u, '').trim()
  return COST_SECTION_DISPLAY_TITLES[raw] ?? COST_SECTION_DISPLAY_TITLES[stripped] ?? raw
}

/** 与报价合计中各段金额算法一致（见 crud `sectionAmountMap`） */
const COST_SECTION_SUBTOTAL_KEYS = new Set(['材料成本', '物料成本', '加工成本', '其它成本', '其他成本'])
function costSectionSubtotalLabel(section: string) {
  const key = String(section ?? '').trim()
  if (!COST_SECTION_SUBTOTAL_KEYS.has(key)) return ''
  const n = sectionAmountMap.value[key] ?? 0
  return `合计：${formatCostStructureSectionTotal(n)}`
}

function displayText(v: unknown) {
  if (v === null || v === undefined) return '—'
  const s = String(v).trim()
  return s || '—'
}

const INQUIRY_FILE_TYPE_ORDER = [1, 2, 3] as const
const INQUIRY_FILE_TYPE_LABELS: Record<number, string> = {
  1: '产品图纸',
  2: '招标文件',
  3: '其它文件'
}

const normalizeInquiryFileType = (raw: unknown): 1 | 2 | 3 => {
  const n = Number(raw)
  if (n === 1 || n === 2 || n === 3) return n
  return 3
}

const inquiryAttachmentHref = (file: InquiryAttachmentRow) => {
  const p = String(file.file_path ?? '').trim()
  if (!p) return '#'
  return getBaseURL(p)
}

const route = useRoute()
const router = useRouter()

/** 仅 `?mode=edit` 为编辑；无 query、点标签页进入等默认查看 */
const pageTitle = computed(() => (route.query.mode === 'edit' ? '编辑报价' : '查看报价'))

const {
  viewQuote,
  openQuote,
  dialog,
  statusTagType,
  statusLabel,
  templateLabel,
  current,
  isReadOnly,
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
  quoteRollupForRfq,
  sectionAmountMap,
  formatCostStructureSectionTotal,
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
  formatMoney,
  saveQuote,
  isQuotationEditable,
  loading
} = useQuoteCrud({
  uiContext: 'detail',
  onSaveSuccess: () => {
    router.back()
  }
})

const goBack = () => {
  router.back()
}

const onQuotationAttachmentListChange = (_file: unknown, fileList: any[]) => {
  current.attachments = fileList
}

const quotationAttachmentHref = (file: any) => {
  const p = String(
    file?.url ?? file?.file_path ?? file?.response?.data?.url ?? file?.response?.url ?? ''
  ).trim()
  if (!p) return '#'
  return getBaseURL(p)
}

const removeQuotationAttachment = (file: any) => {
  const uid = file?.uid
  current.attachments = (current.attachments || []).filter((f: any) => f.uid !== uid)
}

const inquiryAttachmentGroups = computed(() => {
  const list = (current.inquiryAttachments || []) as InquiryAttachmentRow[]
  if (!list.length) return [] as { fileType: number; label: string; items: InquiryAttachmentRow[] }[]
  const byType = new Map<number, InquiryAttachmentRow[]>()
  for (const row of list) {
    const t = normalizeInquiryFileType(row.file_type)
    if (!byType.has(t)) byType.set(t, [])
    byType.get(t)!.push(row)
  }
  return INQUIRY_FILE_TYPE_ORDER.filter((t) => (byType.get(t)?.length ?? 0) > 0).map((t) => {
    const items = byType.get(t)!
    return {
      fileType: t,
      label: items[0]?.file_type_label || INQUIRY_FILE_TYPE_LABELS[t],
      items
    }
  })
})

const quoteSummaryRowClassName = ({ row }: { row: { isSubtotal?: boolean; section?: string } }) => {
  if (!row?.isSubtotal) return ''
  const s = String(row.section || '')
  if (s === '税后总计') return 'quote-summary__subtotal quote-summary__subtotal--posttax'
  if (s === '税前合计') return 'quote-summary__subtotal quote-summary__subtotal--pretax'
  if (s === '成本合计') return 'quote-summary__subtotal quote-summary__subtotal--cost'
  return 'quote-summary__subtotal'
}

const activeTab = ref('base')

async function loadPage() {
  const id = String(route.params.id || '').trim()
  if (!id) {
    goBack()
    return
  }
  const mode = route.query.mode === 'edit' ? 'edit' : 'view'
  dialog.mode = mode
  dialog.quoteId = id
  if (mode === 'view') {
    viewQuote({ id } as any)
  } else {
    await openQuote({ id } as any)
  }
}

watch(
  () => [route.params.id, route.query.mode] as const,
  () => {
    loadPage()
  },
  { immediate: true }
)
</script>

<style scoped>
/* 与杂采询价单详情页（rfqmiscellaneous/detail.vue）布局与风格对齐：fs-page header / 可滚动内容区 / footer */
.quote-detail-page {
  box-sizing: border-box;
}
.quote-detail-page :deep(.fs-page-header) {
  border-bottom: none;
  padding: 0;
  flex-shrink: 0;
}
.quote-detail-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  width: 100%;
  padding: 10px 16px 12px;
  background: linear-gradient(180deg, var(--el-bg-color) 0%, var(--el-fill-color-blank) 100%);
  border-bottom: 1px solid var(--el-border-color-lighter);
}
.quote-detail-toolbar__left {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}
.quote-detail-back {
  padding: 6px 10px 6px 6px;
  color: var(--el-text-color-regular);
}
.quote-detail-back:hover {
  color: var(--el-color-primary);
}
.quote-detail-back__icon {
  margin-right: 2px;
  vertical-align: middle;
}
.quote-detail-toolbar__title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  letter-spacing: 0.02em;
}
.quote-detail-toolbar__meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}
.quote-detail-toolbar__meta-label {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}
.detail-body {
  padding: 12px 0 8px;
  box-sizing: border-box;
  min-height: 0;
}
.detail-card {
  max-width: 1280px;
  margin: 0 auto;
  width: 100%;
  padding: 0 4px;
  box-sizing: border-box;
}
.detail-tabs :deep(.el-tabs__header) {
  margin-bottom: 0;
}
.detail-tabs :deep(.el-tabs__content) {
  padding: 16px 14px 16px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  border-top: none;
  border-radius: 0 0 8px 8px;
}
.detail-tabs :deep(.el-tabs__nav-wrap) {
  padding: 0 4px;
}
.quote-detail-page :deep(.fs-page-footer) {
  flex-shrink: 0;
  border-top: 1px solid var(--el-border-color-lighter);
  background: var(--el-bg-color);
  box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.06);
  padding: 0;
}
.detail-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 10px;
  padding: 12px 20px 14px;
  max-width: 1280px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}
.tabs-fill {
  width: 100%;
}
.tabs-fill :deep(.el-tab-pane) {
  min-height: 280px;
}
.tab-pane-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
/* 三页签统一：与成本结构相同的冷灰渐变底与区块节奏 */
.tab-pane-body.quote-tab-pane {
  gap: 18px;
  padding: 4px 2px 2px;
  border-radius: 10px;
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 38%, transparent 100%);
}
.quote-tab-pane > .quote-descriptions,
.quote-tab-pane > .grid-form.grid-form--edit {
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid rgba(15, 23, 42, 0.08);
  background: linear-gradient(145deg, #ffffff 0%, #fafbfc 100%);
  box-shadow:
    0 1px 2px rgba(15, 23, 42, 0.04),
    0 4px 16px rgba(15, 23, 42, 0.04);
}
.quote-tab-pane > .grid-form.grid-form--edit {
  padding: 16px 18px 18px;
}
.quote-descriptions :deep(.el-descriptions__label) {
  width: 120px;
  font-weight: 500;
  color: var(--el-text-color-secondary);
}
.quote-descriptions :deep(.el-descriptions__content) {
  color: var(--el-text-color-primary);
}
.quote-tab-pane .quote-descriptions :deep(.el-descriptions__label) {
  background: linear-gradient(180deg, #f1f5f9 0%, #e8eef4 100%);
  font-weight: 600;
  color: #475569;
}
.quote-tab-pane .quote-descriptions :deep(.el-descriptions__content) {
  background: #fff;
  color: #0f172a;
}
.section-block {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.section-block__title {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  padding-bottom: 4px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}
.quote-tab-pane .section-block {
  gap: 14px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 10px;
  padding: 16px 18px;
  background: linear-gradient(145deg, #ffffff 0%, #fafbfc 100%);
  box-shadow:
    0 1px 2px rgba(15, 23, 42, 0.04),
    0 4px 16px rgba(15, 23, 42, 0.04);
}
.quote-tab-pane .section-block__title {
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 0.03em;
  color: #0f172a;
  padding-left: 14px;
  margin-left: 2px;
  margin-bottom: 4px;
  border-left: 4px solid #2563eb;
  line-height: 1.35;
  padding-bottom: 0;
  border-bottom: none;
}
.inquiry-attachments {
  border-radius: 8px;
  padding: 10px 12px;
  background: var(--el-fill-color-light);
  border: 1px solid var(--el-border-color-lighter);
}
.quote-tab-pane .inquiry-attachments {
  padding: 12px 14px;
  background: rgba(248, 250, 252, 0.95);
  border: 1px solid rgba(148, 163, 184, 0.28);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.7);
}
.inquiry-attachments__block + .inquiry-attachments__block {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed var(--el-border-color-lighter);
}
.inquiry-attachments__type {
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 6px;
  font-size: 13px;
}
.inquiry-attachments__links {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
}
.inquiry-attachments__link {
  font-size: 13px;
}
.inquiry-attachments__empty {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}
.grid-form {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px 18px;
}
@media (max-width: 1200px) {
  .grid-form {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
@media (max-width: 768px) {
  .grid-form {
    grid-template-columns: 1fr;
  }
}
.grid-form--edit :deep(.el-form-item) {
  margin-bottom: 0;
}
.grid-form--edit :deep(.el-input__wrapper),
.grid-form--edit :deep(.el-select .el-input__wrapper) {
  min-height: 34px;
}
.quote-tab-pane .grid-form--edit :deep(.el-input__wrapper),
.quote-tab-pane .grid-form--edit :deep(.el-select .el-input__wrapper) {
  border-radius: 6px;
}
.w-full {
  width: 100%;
}
.quote-summary {
  display: grid;
  grid-template-columns: 1fr minmax(200px, 240px);
  gap: 14px;
  align-items: stretch;
}
.quote-tab-pane .quote-summary {
  gap: 16px;
}
@media (max-width: 900px) {
  .quote-summary {
    grid-template-columns: 1fr;
  }
}
.quote-summary__total {
  border: 1px solid rgba(15, 23, 42, 0.1);
  border-radius: 10px;
  padding: 14px 16px;
  background: linear-gradient(155deg, #f8fafc 0%, #eff6ff 48%, #f1f5f9 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 8px;
  box-shadow:
    0 1px 2px rgba(15, 23, 42, 0.05),
    inset 0 1px 0 rgba(255, 255, 255, 0.9);
}
.quote-summary__label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  font-weight: 500;
}
.quote-tab-pane .quote-summary__label {
  font-weight: 600;
  color: #64748b;
  letter-spacing: 0.02em;
}
.quote-summary__value {
  font-size: 22px;
  font-weight: 700;
  color: var(--el-text-color-primary);
  line-height: 1.2;
  font-variant-numeric: tabular-nums;
}
.quote-summary__value--pretax {
  font-size: 18px;
  font-weight: 700;
  color: var(--el-text-color-regular);
  font-variant-numeric: tabular-nums;
}
.quote-summary__table {
  border-radius: 8px;
  overflow: hidden;
}
.quote-tab-pane .quote-summary__table :deep(.el-table__header-wrapper th.el-table__cell) {
  background: linear-gradient(180deg, #f1f5f9 0%, #e8eef4 100%) !important;
  color: #334155;
  font-weight: 600;
  font-size: 12px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.35) !important;
}
.quote-tab-pane .quote-summary__table :deep(.el-table__body td.el-table__cell) {
  border-bottom: 1px solid rgba(241, 245, 249, 0.95);
}
.quote-tab-pane .quote-summary__table :deep(.el-table__inner-wrapper::before) {
  display: none;
}
.quote-summary__table :deep(tr.quote-summary__subtotal td) {
  font-weight: 600;
}
.quote-summary__table :deep(tr.quote-summary__subtotal--cost td) {
  background: #fffbeb !important;
  color: #b45309;
  border-left: 4px solid #f59e0b !important;
}
.quote-summary__table :deep(tr.quote-summary__subtotal--pretax td) {
  background: #eff6ff !important;
  color: #1d4ed8;
  border-left: 4px solid #3b82f6 !important;
}
.quote-summary__table :deep(tr.quote-summary__subtotal--posttax td) {
  background: #ecfdf5 !important;
  color: #047857;
  font-weight: 700;
  border-left: 4px solid #10b981 !important;
}
/* —— 成本结构：段内表格、工具栏（页签壳层样式见 .quote-tab-pane） —— */
.cost-toolbar {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding-bottom: 12px;
  margin-bottom: 4px;
  border-bottom: 1px solid rgba(15, 23, 42, 0.06);
}
.cost-toolbar :deep(.el-button) {
  border-radius: 6px;
  font-weight: 500;
}
.cost-groups {
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.cost-group {
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 10px;
  padding: 16px 18px 14px;
  background: linear-gradient(145deg, #ffffff 0%, #fafbfc 100%);
  overflow-x: auto;
  box-shadow:
    0 1px 2px rgba(15, 23, 42, 0.04),
    0 4px 16px rgba(15, 23, 42, 0.04);
}
.cost-group-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 12px;
  padding-bottom: 2px;
}
.cost-group-header__tail {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-shrink: 0;
  margin-left: auto;
}
.cost-group-header__tail :deep(.el-button--small) {
  border-radius: 6px;
  font-weight: 500;
  padding: 6px 14px;
}
.cost-section-subtotal {
  font-size: 13px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  color: #0f172a;
  white-space: nowrap;
  padding: 5px 12px;
  border-radius: 6px;
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
  border: 1px solid rgba(148, 163, 184, 0.45);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8);
  letter-spacing: 0.02em;
}
.cost-totals-footer {
  margin-top: 8px;
  padding: 0;
  border: 1px solid rgba(15, 23, 42, 0.1);
  border-radius: 10px;
  background: linear-gradient(155deg, #f8fafc 0%, #eff6ff 48%, #f1f5f9 100%);
  box-shadow:
    0 1px 2px rgba(15, 23, 42, 0.05),
    inset 0 1px 0 rgba(255, 255, 255, 0.9);
  overflow: hidden;
}
.cost-totals-footer__inner {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0;
  min-height: 88px;
}
@media (max-width: 900px) {
  .cost-totals-footer__inner {
    grid-template-columns: 1fr;
  }
}
.cost-totals-footer__item {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  justify-content: center;
  gap: 8px;
  min-width: 0;
  padding: 16px 20px;
  border-right: 1px solid rgba(148, 163, 184, 0.25);
  background: rgba(255, 255, 255, 0.35);
}
.cost-totals-footer__item:last-child {
  border-right: none;
}
@media (max-width: 900px) {
  .cost-totals-footer__item {
    border-right: none;
    border-bottom: 1px solid rgba(148, 163, 184, 0.25);
  }
  .cost-totals-footer__item:last-child {
    border-bottom: none;
  }
}
.cost-totals-footer__label {
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  letter-spacing: 0.04em;
  text-transform: none;
}
.cost-totals-footer__value {
  font-size: 22px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  color: #0f172a;
  line-height: 1.2;
  letter-spacing: 0.02em;
}
.cost-row-pair {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 18px;
}
.cost-section-title {
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 0.03em;
  color: #0f172a;
  padding-left: 14px;
  margin-left: 2px;
  border-left: 4px solid #2563eb;
  line-height: 1.35;
}
/* 段内表格：表头冷灰、圆角、金额列更易扫读 */
.cost-el-table {
  border-radius: 8px;
  overflow: hidden;
}
.quote-tab-pane .cost-el-table :deep(.el-table__header-wrapper th.el-table__cell) {
  background: linear-gradient(180deg, #f1f5f9 0%, #e8eef4 100%) !important;
  color: #334155;
  font-weight: 600;
  font-size: 12px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.35) !important;
}
.quote-tab-pane .cost-el-table :deep(.el-table__body td.el-table__cell) {
  border-bottom: 1px solid rgba(241, 245, 249, 0.95);
}
.quote-tab-pane .cost-el-table :deep(.el-table__inner-wrapper::before) {
  display: none;
}
.compact-cost-table :deep(.el-table__cell) {
  padding: 8px 10px;
}
.compact-cost-table :deep(.el-input__wrapper) {
  min-height: 32px;
}
.quote-tab-pane .cost-el-table :deep(.el-input__wrapper) {
  border-radius: 6px;
  box-shadow: none;
  transition: box-shadow 0.15s ease, border-color 0.15s ease;
}
.quote-tab-pane .cost-el-table :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px rgba(37, 99, 235, 0.2) inset;
}
.attach-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  align-items: start;
}
.quote-tab-pane .attach-row :deep(.el-upload-dragger) {
  border-radius: 8px;
  border-color: rgba(148, 163, 184, 0.45);
  background: rgba(248, 250, 252, 0.65);
}
.quote-tab-pane .attach-row :deep(.el-textarea .el-textarea__inner) {
  border-radius: 8px;
}
@media (max-width: 768px) {
  .attach-row {
    grid-template-columns: 1fr;
  }
}
.attach-readonly__list {
  margin: 0;
  padding-left: 18px;
  color: var(--el-text-color-primary);
  font-size: 13px;
}
.attach-readonly__item {
  margin-bottom: 4px;
}
.attach-readonly__empty {
  margin: 0;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}
.attach-readonly__remark-wrap {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed var(--el-border-color-lighter);
}
.attach-readonly__remark-label {
  display: block;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-bottom: 4px;
}
.attach-readonly__remark {
  margin: 0;
  font-size: 13px;
  line-height: 1.6;
  color: var(--el-text-color-primary);
  white-space: pre-wrap;
}
.quotation-upload-file {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 4px;
}
.quotation-upload-file__name {
  font-size: 13px;
  color: var(--el-text-color-regular);
}
.quotation-upload-file__link {
  font-size: 13px;
}
.mb12 {
  margin-bottom: 12px;
}
</style>
