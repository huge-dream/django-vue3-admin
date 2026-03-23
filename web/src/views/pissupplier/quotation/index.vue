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

    <el-dialog v-model="dialog.visible" width="1080px" :title="dialogTitle">
      <div class="status-bar">
        <span>报价状态：</span>
        <el-tag :type="statusTagType(current.status)">{{ statusLabel(current.status) }}</el-tag>
      </div>

      <el-tabs v-model="activeTab" type="card" class="tabs-fill">
        <el-tab-pane label="基础信息" name="base">
          <el-divider content-position="left">关联询价信息</el-divider>
          <el-descriptions :column="3" border size="small" class="mb8">
            <el-descriptions-item label="询价单号">{{ current.inquiryCode }}</el-descriptions-item>
            <el-descriptions-item label="询价单名称">{{ current.inquiryTitle }}</el-descriptions-item>
            <el-descriptions-item label="询价模板">{{ templateLabel(current.template) }}</el-descriptions-item>
            <el-descriptions-item label="交易币别">{{ current.currency }}</el-descriptions-item>
            <el-descriptions-item label="报价截止日">{{ current.quoteDeadline }}</el-descriptions-item>
            <el-descriptions-item label="询价状态">{{ current.inquiryStatus }}</el-descriptions-item>
          </el-descriptions>

          <el-divider content-position="left">报价基础信息</el-divider>
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
              <div class="quote-summary__label">最终报价</div>
              <div class="quote-summary__value">{{ formatMoney(quoteTotal) }}</div>
            </div>
          </div>

          <el-divider content-position="left">报价附件与说明</el-divider>
          <div class="attach-row">
            <el-upload
              action="#"
              :auto-upload="false"
              :file-list="current.attachments"
              :disabled="isReadOnly"
              list-type="text"
              drag
            >
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

      <template #footer>
        <el-button @click="dialog.visible = false">关闭</el-button>
        <template v-if="!isReadOnly && isPendingQuotation(current)">
          <el-button type="primary" @click="saveQuote">保存</el-button>
        </template>
      </template>
    </el-dialog>
  </fs-page>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { Flag } from '@element-plus/icons-vue'
import { compute, dict, useCrud, useExpose } from '@fast-crud/fast-crud'
import { useQuoteCrud, formatAwardBidStatus } from './crud'

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

const quoteSummaryRowClassName = ({ row }: { row: { isSubtotal?: boolean } }) =>
  row?.isSubtotal ? 'quote-summary__subtotal' : ''

const activeTab = ref('base')

const syncFilters = (form: any = {}) => {
  filters.status = form.status || ''
  filters.quoteNo = form.quoteNo || ''
  filters.inquiryCode = form.inquiryCode || ''
  filters.inquiryTitle = form.inquiryTitle || ''
  filters.currency = form.currency || ''
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
        text: '编辑报价',
        type: 'primary',
        show: compute(({ row }) => isPendingQuotation(row)),
        click: ({ row }: any) => openQuote(row)
      },
      editQuote: {
        text: '提交报价',
        type: 'warning',
        show: compute(({ row }) => isPendingQuotation(row)),
        click: ({ row }: any) => submitQuotationFromRow(row)
      },
    }
  },
  columns: {
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
      column: { width: 180 }
    },
    status: {
      title: '报价状态',
      type: 'dict-select',
      dict: dict({ data: statusOptions }),
      search: { show: true },
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
.status-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f8fafc;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 8px 12px;
  margin-bottom: 8px;
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
.quote-summary__table {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}
.quote-summary__table :deep(tr.quote-summary__subtotal td) {
  font-weight: 600;
  background-color: var(--el-fill-color-light);
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
