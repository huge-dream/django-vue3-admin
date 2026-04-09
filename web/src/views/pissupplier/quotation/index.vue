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
  </fs-page>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Flag } from '@element-plus/icons-vue'
import { compute, dict, useCrud, useExpose } from '@fast-crud/fast-crud'
import {
  useQuoteCrud,
  formatAwardBidStatus,
  buyingMethodDict,
  formatBidTimeColumn,
  formatQuoteDeadlineDisplay,
  isWithinSupplierBidWindow,
  getSupplierBidWindowRejectReason
} from './crud'

const { t } = useI18n()

/** 查询区：按主表 is_awarded 筛选（与后端字段一致） */
const isAwardedOptions = [
  { label: t('message.pages.pissupplier.quotation.awarded'), value: 1 },
  { label: t('message.pages.pissupplier.quotation.notAwarded'), value: 0 }
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
const router = useRouter()

const {
  filters,
  statusOptions,
  filteredQuotes,
  loadQuotes,
  isPendingQuotation,
  isQuotedQuotation,
  statusTagType,
  statusLabel,
  templateLabel,
  formatMoney,
  submitQuotationFromRow
} = useQuoteCrud({ onChange: () => crudExpose?.doRefresh?.() })

/** 使「招标」行操作按钮随当前时间进出投标窗口自动刷新（约 30s） */
const bidWindowClock = ref(0)
let bidWindowTimer: ReturnType<typeof setInterval> | undefined

function goQuoteDetail(row: { id: string }, mode: 'edit' | 'view') {
  router.push({
    name: 'PissupplierQuotationDetail',
    params: { id: row.id },
    query: { mode }
  })
}

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
  table: { rowKey: 'id', size: 'medium' },
  rowHandle: {
    fixed: 'right',
    width: 240,
    buttons: {
      // Hide fast-crud default actions; use custom actions below instead
      view: { show: false },
      edit: { show: false },
      remove: { show: false },
      viewInquiry: {
        text: t('message.pages.pissupplier.quotation.view'),
        click: ({ row }: any) => goQuoteDetail(row, 'view')
      },
      quoteNow: {
        text: t('message.pages.pissupplier.quotation.quoteNow'),
        type: compute(({ row }) => {
          bidWindowClock.value
          const ok = isPendingQuotation(row)
          return ok ? 'primary' : 'info'
        }),
        show: true,
        click: ({ row }: any) => {
          const bidReason = getSupplierBidWindowRejectReason(row)
          if (bidReason) {
            ElMessage.warning(bidReason)
            return
          }
          goQuoteDetail(row, 'edit')
        },
        disabled: compute(({ row }) => {
          bidWindowClock.value
          return !isPendingQuotation(row)
        })
      },
      editQuote: {
        text: t('message.pages.pissupplier.quotation.submitQuote'),
        type: compute(({ row }) => {
          bidWindowClock.value
          const ok = isQuotedQuotation(row) && isWithinSupplierBidWindow(row)
          return ok ? 'warning' : 'info'
        }),
        show: true,
        click: ({ row }: any) => submitQuotationFromRow(row),
        disabled: compute(({ row }) => {
          bidWindowClock.value
          return !isQuotedQuotation(row) || !isWithinSupplierBidWindow(row)
        })
      },
    }
  },
  columns: {
    inquiryPlant: {
      title: t('message.pages.pissupplier.quotation.companyShortName'),
      type: 'text',
      search: {
        show: true,
        component: { props: { clearable: true, placeholder: t('message.pages.pissupplier.quotation.companyCodeOrName') } }
      },
      column: { show: false }
    },
    companyShortName: {
      title: t('message.pages.pissupplier.quotation.companyShortName'),
      type: 'text',
      search: { show: false },
      column: { minWidth: 100, showOverflowTooltip: true }
    },
    buyingMethod: {
      title: t('message.pages.pissupplier.quotation.buyingMethod'),
      type: 'dict-select',
      dict: dict({ data: buyingMethodDict(t) }),
      search: {
        show: true,
        component: { props: { placeholder: t('message.pages.pissupplier.quotation.buyingMethod'), clearable: true } }
      },
      column: {
        width: 100,
        formatter: ({ row, value }: any) => {
          const v = value ?? row?.buyingMethod
          const n = Number(v)
          if (!Number.isFinite(n)) return v != null && v !== '' ? String(v) : ''
          return buyingMethodDict(t).find((d: any) => d.value === n)?.label ?? String(v)
        }
      }
    },
    quoteNo: {
      title: t('message.pages.pissupplier.quotation.quotationNo'),
      type: 'text',
      search: { show: true, component: { props: { clearable: true, placeholder: t('message.pages.pissupplier.quotation.quotationNo') } } },
      column: { minWidth: 120, showOverflowTooltip: true }
    },
    inquiryCode: {
      title: t('message.pages.pissupplier.quotation.inquiryNo'),
      type: 'text',
      search: { show: true, component: { props: { clearable: true, placeholder: t('message.pages.pissupplier.quotation.inquiryNo') } } },
      column: { minWidth: 120, showOverflowTooltip: true }
    },
    inquiryTitle: {
      title: t('message.pages.pissupplier.quotation.inquiryTitle'),
      type: 'text',
      search: { show: true, component: { props: { clearable: true, placeholder: t('message.pages.pissupplier.quotation.inquiryTitle') } } },
      column: { minWidth: 100, showOverflowTooltip: true }
    },
    template: {
      title: t('message.pages.pissupplier.quotation.inquiryTemplate'),
      type: 'text',
      column: {
        minWidth: 100,
        showOverflowTooltip: true,
        formatter: ({ value }: any) => templateLabel(value)
      }
    },
    quoteDeadline: {
      title: t('message.pages.pissupplier.quotation.quoteDeadline'),
      type: 'datetime',
      search: {
        show: true,
        component: {
          name: 'el-date-picker',
          props: {
            type: 'daterange',
            rangeSeparator: t('message.pages.pissupplier.quotation.quoteDeadlineSeparator'),
            startPlaceholder: t('message.pages.pissupplier.quotation.quoteDeadlineStart'),
            endPlaceholder: t('message.pages.pissupplier.quotation.quoteDeadlineEnd'),
            valueFormat: 'YYYY-MM-DD'
          }
        }
      },
      column: { width: 150, formatter: ({ value }: any) => formatQuoteDeadlineDisplay(value) }
    },
    bidStartTime: {
      title: t('message.pages.pissupplier.quotation.bidStartTime'),
      type: 'datetime',
      column: {
        width: 150,
        formatter: ({ row, value }: any) => formatBidTimeColumn(row, value)
      }
    },
    bidEndTime: {
      title: t('message.pages.pissupplier.quotation.bidEndTime'),
      type: 'datetime',
      column: {
        width: 150,
        formatter: ({ row, value }: any) => formatBidTimeColumn(row, value)
      }
    },
    status: {
      title: t('message.pages.pissupplier.quotation.quoteStatus'),
      type: 'dict-select',
      dict: dict({ data: statusOptions }),
      search: { show: false },
      column: { width: 100, slots: { default: 'cell_status' } }
    },
    isAwarded: {
      title: t('message.pages.pissupplier.quotation.isAwarded'),
      type: 'dict-select',
      dict: dict({ data: isAwardedOptions }),
      search: {
        show: true,
        component: { props: { placeholder: t('message.pages.pissupplier.quotation.isAwardedSearchPlaceholder'), clearable: true } }
      },
      column: { width: 100, slots: { default: 'cell_isAwarded' } }
    },
    quoteTime: {
      title: t('message.pages.pissupplier.quotation.quoteTime'),
      type: 'datetime',
      column: { width: 180 }
    },
    quoteAmount: {
      title: t('message.pages.pissupplier.quotation.quoteAmount'),
      type: 'text',
      column: { width: 120, slots: { default: 'cell_quoteAmount' } }
    },
    currency: {
      title: t('message.pages.pissupplier.quotation.currency'),
      type: 'text',
      search: { show: true, component: { props: { placeholder: t('message.pages.pissupplier.quotation.currency'), clearable: true } } },
      column: { width: 90 }
    },
    createdAt: {
      title: t('message.pages.pissupplier.quotation.createTime'),
      type: 'datetime',
      column: { width: 180 }
    }
  }
}

useCrud({ crudRef, crudBinding, crudExpose, crudOptions })

onMounted(() => {
  bidWindowTimer = setInterval(() => {
    bidWindowClock.value += 1
  }, 30000)
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
</style>
