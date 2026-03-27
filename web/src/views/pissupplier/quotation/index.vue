<template>
  <fs-page class="quote-page">
    <fs-crud ref="crudRef" v-bind="crudBinding">
      <template #cell_status="{ row }">
        <el-tag :type="statusTagType(row.status)">{{ statusLabel(row.status) }}</el-tag>
      </template>
      <template #cell_isAwarded="{ row }">
        <span v-if="awardBidIsFlag(row)" class="award-bid-flag-row">
          <span class="award-bid-text award-bid-flag-label">{{ awardBidFlagText(row) }}</span>
          <el-icon class="award-flag" color="#f59e0b" :size="18">
            <Flag />
          </el-icon>
        </span>
        <span v-else class="award-bid-text">{{ awardBidText(row) }}</span>
      </template>
      <template #cell_quoteAmount="{ row }">
        {{ formatMoney(row.quoteAmount) }}
      </template>
    </fs-crud>

    <el-dialog v-model="dialog.visible" width="1080px" :title="dialogTitle" class="quote-dialog-el">
      <div class="quote-dialog-scroll" :style="{ '--quote-sticky-status-h': `${quoteStickyStatusHeightPx}px` }">
        <!-- 整块粘性顶栏：间距放在壳子内，避免 margin 在 sticky 外形成透明缝导致滚动内容透出 -->
        <div ref="quoteStickyStatusShellRef" class="quote-dialog-sticky-status">
          <div class="status-bar">
            <span>报价状态：</span>
            <el-tag :type="statusTagType(current.status)">{{ statusLabel(current.status) }}</el-tag>
          </div>
        </div>

        <el-tabs v-model="activeTab" type="card" class="tabs-fill quote-dialog-tabs">
          <el-tab-pane label="询价单信息" name="inquiry">
            <el-divider content-position="left"></el-divider>
            <div class="inquiry-tab-pane">
              <el-form class="grid-form inquiry-form-readonly" label-width="120px">
                <el-form-item label="询价单号">
                  <el-input :model-value="current.inquiryCode" disabled />
                </el-form-item>
                <el-form-item label="询价单名称">
                  <el-input :model-value="current.inquiryTitle" disabled />
                </el-form-item>
                <el-form-item label="询价模板">
                  <el-input :model-value="templateLabel(current.template)" disabled />
                </el-form-item>
                <el-form-item label="交易币别">
                  <el-input :model-value="current.currency" disabled />
                </el-form-item>
                <el-form-item label="报价截止日">
                  <el-input :model-value="current.quoteDeadline" disabled />
                </el-form-item>
                <el-form-item label="交易厂区">
                  <el-input :model-value="current.companyShortName || current.inquiryCompanyCode || '—'" disabled />
                </el-form-item>
              </el-form>
              <el-divider content-position="left">询价附件</el-divider>
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
          </el-tab-pane>

          <el-tab-pane label="报价基础信息" name="base">
            <el-divider content-position="left"></el-divider>
            <el-form :model="current.base" label-width="120px" class="grid-form">
              <el-form-item label="联系人">
                <el-input v-model="current.base.contact" :disabled="isReadOnly" />
              </el-form-item>
              <el-form-item label="联系电话">
                <el-input v-model="current.base.phone" :disabled="isReadOnly" />
              </el-form-item>
              <el-form-item label="联系邮箱">
                <el-input v-model="current.base.email" :disabled="isReadOnly" />
              </el-form-item>
              <el-form-item label="报价有效期(天)">
                <el-input v-model="current.base.validityDays" type="number" :disabled="isReadOnly" />
              </el-form-item>
              <el-form-item label="交货周期(天)">
                <el-input v-model="current.base.leadTimeDays" type="number" :disabled="isReadOnly" />
              </el-form-item>
              <el-form-item label="付款方式">
                <el-select v-model="current.base.paymentTerm" placeholder="选择付款方式" :disabled="isReadOnly">
                  <el-option label="T/T 30%预付，70%出货前" value="tt_30_70" />
                  <el-option label="月结30天" value="net30" />
                  <el-option label="月结45天" value="net45" />
                  <el-option label="全额预付" value="prepaid" />
                </el-select>
              </el-form-item>
            </el-form>

            <el-divider content-position="left">报价合计</el-divider>
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

            <el-divider content-position="left">报价附件与说明</el-divider>
            <div class="attach-row">
              <el-upload
                action="#"
                :auto-upload="false"
                multiple
                list-type="text"
                drag
                :disabled="isReadOnly"
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
                      v-if="!isReadOnly"
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
              <el-input v-model="current.remark" type="textarea" :rows="4" placeholder="补充报价说明" :disabled="isReadOnly" />
            </div>
          </el-tab-pane>

          <el-tab-pane label="成本结构" name="cost">
            <div class="cost-header mb8">
              <span></span>
              <el-button size="small" @click="loadCostRowsFromTemplate(current.templateSections, true)" :disabled="isReadOnly">清空已填内容</el-button>
            </div>
            <div class="cost-groups">
              <div v-for="section in primarySections" :key="section" class="cost-group">
                <div class="cost-group-header">
                  <div class="cost-section-title">{{ section }}</div>
                  <!-- 显隐由 sectionAddConfig 控制：材料/加工对应模板 is_can_add_materials / is_can_add_process（详情 template_sections[].supplierCanAddRow） -->
                  <el-button
                    size="small"
                    type="primary"
                    @click="addCostRow(section)"
                    v-if="sectionAddConfig[section] && !isReadOnly"
                  >新增一行</el-button>
                </div>
                <el-table
                  :data="(groupedCostRows[section] || [])"
                  border
                  size="small"
                  :class="section === '其它成本' ? 'compact-cost-table' : ''"
                  class="mb12"
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
                    <div class="cost-section-title">{{ section }}</div>
                  </div>
                  <el-table :data="(groupedCostRows[section] || [])" border size="small" class="mb12">
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
          </el-tab-pane>

        </el-tabs>
      </div>

      <template #footer>
        <el-button @click="dialog.visible = false">关闭</el-button>
        <template v-if="!isReadOnly && isQuotationEditable(current)">
          <el-button type="primary" @click="saveQuote">保存</el-button>
        </template>
      </template>
    </el-dialog>
  </fs-page>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { Flag } from '@element-plus/icons-vue'
import { compute, dict, useCrud, useExpose } from '@fast-crud/fast-crud'
import { getBaseURL } from '/@/utils/baseUrl'
import {
  useQuoteCrud,
  formatAwardBidStatus,
  type InquiryAttachmentRow,
  buyingMethodDict,
  formatBidTimeColumn
} from './crud'

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

/** 查询区：按主表 is_awarded 筛选（与后端字段一致） */
const isAwardedOptions = [
  { label: '已中标', value: 1 },
  { label: '未中标', value: 0 }
]

const awardBidIsFlag = (row: any) => formatAwardBidStatus(row).mode === 'flag'
const awardBidFlagText = (row: any) => {
  const r = formatAwardBidStatus(row)
  return r.mode === 'flag' ? r.text : ''
}
const awardBidText = (row: any) => {
  const r = formatAwardBidStatus(row)
  return r.mode === 'text' ? r.text : ''
}

const crudRef = ref()
const crudBinding = ref()
const { crudExpose } = useExpose({ crudRef, crudBinding })

const {
  filters,
  statusOptions,
  filteredQuotes,
  loadQuotes,
  isPendingQuotation,
  isQuotedQuotation,
  isQuotationEditable,
  viewQuote,
  openQuote,
  dialog,
  dialogTitle,
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
  submitQuotationFromRow
} = useQuoteCrud({ onChange: () => crudExpose?.doRefresh?.() })

const onQuotationAttachmentListChange = (_file: unknown, fileList: any[]) => {
  current.attachments = fileList
}

/** 报价附件：与 `buildQuotationAttachmentsForSave` 取路径逻辑一致 */
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

const quoteStickyStatusShellRef = ref<HTMLElement | null>(null)
/** 与页签头部 `top` 对齐：状态条壳实际高度（ResizeObserver 更新） */
const quoteStickyStatusHeightPx = ref(52)
let quoteStickyStatusRo: ResizeObserver | null = null

function measureQuoteStickyStatusShell() {
  nextTick(() => {
    const el = quoteStickyStatusShellRef.value
    if (!el) return
    const h = Math.ceil(el.getBoundingClientRect().height)
    if (h > 0) quoteStickyStatusHeightPx.value = h
  })
}

watch(
  () => dialog.visible,
  async (vis) => {
    if (!vis) {
      quoteStickyStatusRo?.disconnect()
      return
    }
    await nextTick()
    measureQuoteStickyStatusShell()
    const shell = quoteStickyStatusShellRef.value
    if (shell && typeof ResizeObserver !== 'undefined') {
      quoteStickyStatusRo?.disconnect()
      quoteStickyStatusRo = new ResizeObserver(() => measureQuoteStickyStatusShell())
      quoteStickyStatusRo.observe(shell)
    }
  }
)

watch(activeTab, () => {
  if (dialog.visible) measureQuoteStickyStatusShell()
})

onUnmounted(() => {
  quoteStickyStatusRo?.disconnect()
  quoteStickyStatusRo = null
})

const syncFilters = (form: any = {}) => {
  filters.inquiryPlant = form.inquiryPlant || ''
  filters.quoteNo = form.quoteNo || ''
  filters.inquiryCode = form.inquiryCode || ''
  filters.inquiryTitle = form.inquiryTitle || ''
  filters.currency = form.currency || ''
  filters.buyingMethod =
    form.buyingMethod !== undefined && form.buyingMethod !== null && form.buyingMethod !== ''
      ? form.buyingMethod
      : ''
  filters.isAwarded =
    form.isAwarded !== undefined && form.isAwarded !== null && form.isAwarded !== '' ? form.isAwarded : ''
  if (Array.isArray(form.quoteDeadline) && form.quoteDeadline.length === 2) {
    filters.dateRange = form.quoteDeadline as any
  } else if (!form.quoteDeadline) {
    filters.dateRange = [] as any
  }
}

const buildPageRequest = async (query: any) => {
  const page = query?.currentPage || query?.page || 1
  const pageSize = query?.pageSize || query?.page_size || 20
  const form = query?.form || query?.where || query?.query || {}
  syncFilters(form)
  await loadQuotes()
  const list = filteredQuotes.value
  const start = (page - 1) * pageSize
  const end = start + pageSize
  return {
    records: list.slice(start, end),
    total: list.length,
    currentPage: page,
    pageSize
  }
}

const crudOptions = {
  request: {
    pageRequest: buildPageRequest,
    transformRes: ({ res }: any) => res
  },
  form: { labelWidth: '110px' },
  search: { show: true, labelWidth: '90px' },
  actionbar: { show: false },
  table: { rowKey: 'id', size: 'small' },
  rowHandle: {
    fixed: 'right',
    width: 320,
    buttons: {
      // Hide fast-crud default actions; use custom actions below instead
      view: { show: false },
      edit: { show: false },
      remove: { show: false },
      viewInquiry: {
        text: '查看',
        click: ({ row }: any) => viewQuote(row)
      },
      quoteNow: {
        text: '报价',
        type: compute(({ row }) => (isPendingQuotation(row) ? 'primary' : 'info')),
        show: true,
        click: ({ row }: any) => openQuote(row),
        disabled: compute(({ row }) => !isPendingQuotation(row))
      },
      editQuote: {
        text: '提交',
        type: compute(({ row }) => (isQuotedQuotation(row) ? 'warning' : 'info')),
        show: true,
        click: ({ row }: any) => submitQuotationFromRow(row),
        disabled: compute(({ row }) => !isQuotedQuotation(row))
      },
    }
  },
  columns: {
    inquiryPlant: {
      title: '交易厂区',
      type: 'text',
      search: {
        show: true,
        component: { props: { clearable: true, placeholder: '公司代码或简称' } }
      },
      column: { show: false }
    },
    companyShortName: {
      title: '交易厂区',
      type: 'text',
      search: { show: false },
      column: { minWidth: 100, showOverflowTooltip: true }
    },
    buyingMethod: {
      title: '采购方式',
      type: 'dict-select',
      dict: dict({ data: buyingMethodDict }),
      search: {
        show: true,
        component: { props: { placeholder: '采购方式', clearable: true } }
      },
      column: {
        width: 100,
        formatter: ({ row, value }: any) => {
          const v = value ?? row?.buyingMethod
          const n = Number(v)
          if (!Number.isFinite(n)) return v != null && v !== '' ? String(v) : ''
          return buyingMethodDict.find((d) => d.value === n)?.label ?? String(v)
        }
      }
    },
    quoteNo: {
      title: '报价单号',
      type: 'text',
      search: { show: true, component: { props: { clearable: true } } },
      column: { minWidth: 120, showOverflowTooltip: true }
    },
    inquiryCode: {
      title: '询价单号',
      type: 'text',
      search: { show: true, component: { props: { clearable: true } } },
      column: { minWidth: 120, showOverflowTooltip: true }
    },
    inquiryTitle: {
      title: '询价名称',
      type: 'text',
      search: { show: true, component: { props: { clearable: true } } },
      column: { minWidth: 100, showOverflowTooltip: true }
    },
    template: {
      title: '询价模板',
      type: 'text',
      column: {
        minWidth: 100,
        showOverflowTooltip: true,
        formatter: ({ value }: any) => templateLabel(value)
      }
    },
    quoteDeadline: {
      title: '报价截止日',
      type: 'datetime',
      search: {
        show: true,
        component: {
          name: 'el-date-picker',
          props: {
            type: 'daterange',
            rangeSeparator: '至',
            startPlaceholder: '开始日期',
            endPlaceholder: '结束日期',
            valueFormat: 'YYYY-MM-DD'
          }
        }
      },
      column: { width: 150 }
    },
    bidStartTime: {
      title: '投标开始时间',
      type: 'datetime',
      column: {
        width: 150,
        formatter: ({ row, value }: any) => formatBidTimeColumn(row, value)
      }
    },
    bidEndTime: {
      title: '投标截止时间',
      type: 'datetime',
      column: {
        width: 150,
        formatter: ({ row, value }: any) => formatBidTimeColumn(row, value)
      }
    },
    status: {
      title: '报价状态',
      type: 'dict-select',
      dict: dict({ data: statusOptions }),
      search: { show: false },
      column: { width: 100, slots: { default: 'cell_status' } }
    },
    isAwarded: {
      title: '中标状态',
      type: 'dict-select',
      dict: dict({ data: isAwardedOptions }),
      search: { show: true },
      column: { width: 100, slots: { default: 'cell_isAwarded' } }
    },
    quoteTime: {
      title: '报价时间',
      type: 'datetime',
      column: { width: 180 }
    },
    quoteAmount: {
      title: '报价金额',
      type: 'text',
      column: { width: 120, slots: { default: 'cell_quoteAmount' } }
    },
    currency: {
      title: '币别',
      type: 'text',
      search: { show: true, component: { props: { placeholder: '币别', clearable: true } } },
      column: { width: 90 }
    },
    createdAt: {
      title: '创建时间',
      type: 'datetime',
      column: { width: 180 }
    }
  }
}

useCrud({ crudRef, crudBinding, crudExpose, crudOptions })

onMounted(() => {
  crudExpose?.doRefresh?.()
})
</script>

<style scoped>
.award-bid-flag-row {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  vertical-align: middle;
}
.award-bid-flag-label {
  color: #b45309;
  font-weight: 600;
}
.award-flag {
  vertical-align: middle;
}
.award-bid-text {
  font-size: 13px;
  color: #606266;
}
.page {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}
.sub {
  margin: 2px 0 0;
  color: #6b7280;
  font-size: 13px;
}
.actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.list-card {
  border: 1px solid #e5e7eb;
}
.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
/* 弹窗内单独滚动；顶栏粘性区域用不透明背景盖住下方滚动内容 */
.quote-dialog-el :deep(.el-dialog__body) {
  padding-top: 12px;
  padding-bottom: 8px;
}
/* 与 max-height 相同，避免短内容页签（如询价单信息）把弹窗整体压矮 */
.quote-dialog-scroll {
  min-height: min(72vh, calc(100vh - 200px));
  max-height: min(72vh, calc(100vh - 200px));
  overflow-x: hidden;
  overflow-y: auto;
  margin: 0;
  padding: 0 0 12px 0;
  background: var(--el-bg-color, #fff);
  isolation: isolate;
}
.inquiry-tab-pane {
  display: flex;
  flex-direction: column;
  min-height: 100%;
}
.inquiry-form-readonly :deep(.el-form-item) {
  margin-bottom: 0;
}
.inquiry-form-readonly :deep(.el-input.is-disabled .el-input__wrapper) {
  box-shadow: 0 0 0 1px var(--el-border-color) inset;
  background-color: var(--el-fill-color-blank);
}
.inquiry-form-readonly :deep(.el-input.is-disabled .el-input__inner) {
  color: var(--el-text-color-primary);
  -webkit-text-fill-color: var(--el-text-color-primary);
}
.quote-dialog-sticky-status {
  position: sticky;
  top: 0;
  z-index: 22;
  margin: 0 0 0 0;
  padding: 0 0 10px 0;
  background: var(--el-bg-color, #fff);
  background-clip: padding-box;
}
.inquiry-attachments {
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 10px 12px;
  background: var(--el-fill-color-blank);
}
.inquiry-attachments__block + .inquiry-attachments__block {
  margin-top: 12px;
  padding-top: 12px;
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
.status-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--el-fill-color-light, #f5f7fa);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 10px 12px;
  margin: 0;
  box-shadow: none;
}
.quote-dialog-tabs.tabs-fill {
  display: flex;
  flex-direction: column;
}
.quote-dialog-tabs.tabs-fill :deep(.el-tabs__content) {
  flex: 1;
  position: relative;
  z-index: 1;
  padding-top: 4px;
}
.quote-dialog-tabs.tabs-fill :deep(.el-tab-pane) {
  min-height: 0;
}
.quote-dialog-tabs :deep(.el-tabs__header) {
  position: sticky;
  /* 与上方 `.quote-dialog-sticky-status` 实测高度对齐，避免夹缝 */
  top: var(--quote-sticky-status-h, 52px);
  z-index: 21;
  margin: 0;
  padding: 0 0 10px 0;
  background: var(--el-bg-color, #fff);
  background-clip: padding-box;
  border-bottom: 1px solid var(--el-border-color-lighter);
  box-shadow: 0 6px 10px -4px rgba(15, 23, 42, 0.08);
}
.quote-dialog-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none;
}
.grid-form {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px 16px;
}
.quote-summary {
  display: grid;
  grid-template-columns: 1fr 260px;
  gap: 12px;
  align-items: stretch;
}
.quote-summary__total {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px;
  background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 6px;
}
.quote-summary__label {
  color: #2563eb;
  font-weight: 600;
}
.quote-summary__value {
  font-size: 22px;
  font-weight: 700;
  color: #0f172a;
}
.quote-summary__value--pretax {
  font-size: 18px;
  font-weight: 700;
  color: #1e3a5f;
}
.quote-summary__table {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}
/* 报价合计：小计行用分色高亮（替代浅灰） */
.quote-summary__table :deep(tr.quote-summary__subtotal td) {
  font-weight: 700;
}
.quote-summary__table :deep(tr.quote-summary__subtotal--cost td) {
  background: linear-gradient(90deg, #ffedd5 0%, #fff7ed 55%, #fff 100%) !important;
  color: #9a3412;
  border-color: #fdba74 !important;
}
.quote-summary__table :deep(tr.quote-summary__subtotal--pretax td) {
  background: linear-gradient(90deg, #bfdbfe 0%, #dbeafe 55%, #eff6ff 100%) !important;
  color: #1e40af;
  border-color: #93c5fd !important;
}
.quote-summary__table :deep(tr.quote-summary__subtotal--posttax td) {
  background: linear-gradient(90deg, #6ee7b7 0%, #a7f3d0 45%, #d1fae5 100%) !important;
  color: #065f46;
  font-weight: 800;
  border-color: #34d399 !important;
}
.cost-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
  color: #4b5563;
}
.cost-groups {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.cost-group {
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 12px;
  background: #fff;
  overflow-x: auto;
}
.cost-group-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}
.cost-row-pair {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
  gap: 12px;
}
.cost-section-title {
  font-weight: 600;
  margin-bottom: 4px;
  color: #111827;
}
.compact-cost-table :deep(.el-table__cell) {
  padding: 6px 8px;
}
.compact-cost-table :deep(.el-input__wrapper) {
  min-height: 30px;
}
.attach-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  align-items: start;
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
.w-260 {
  width: 260px;
}
.w-160 {
  width: 160px;
}
.w-280 {
  width: 280px;
}
</style>
