<template>
  <fs-page>
    <fs-crud ref="crudRef" v-bind="crudBinding" />
  </fs-page>
</template>

<script setup lang="ts" name="InquiryManagement">
import { onActivated, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useCrud, useExpose } from '@fast-crud/fast-crud'
import { createCrudOptions } from './crud'

const crudRef = ref()
const crudBinding = ref()
const { crudExpose } = useExpose({ crudRef, crudBinding })

const selectedInquiryRows = ref<any[]>([])
const router = useRouter()

function goCreate() {
  router.push({
    name: 'PisadminRfqMiscInquiryDetail',
    params: { id: 'new' },
    query: { mode: 'create' }
  })
}
function goEdit(row: any) {
  router.push({
    name: 'PisadminRfqMiscInquiryDetail',
    params: { id: String(row.id) },
    query: { mode: 'edit' }
  })
}
function goView(row: any) {
  router.push({
    name: 'PisadminRfqMiscInquiryDetail',
    params: { id: String(row.id) },
    query: { mode: 'view' }
  })
}

/** 跳转杂采比价/议价路由页（`/comparePrice/:id`） */
const openComparison = (row: any) => {
  router.push({
    name: 'PisadminRfqMiscComparePrice',
    params: { id: String(row.id) }
  })
}

const { crudOptions } = createCrudOptions({
  crudExpose,
  onAdd: goCreate,
  onEdit: goEdit,
  onView: goView,
  onComparison: openComparison,
  onTableSelectionChange: (rows) => {
    selectedInquiryRows.value = rows || []
  },
  getTableSelection: () => selectedInquiryRows.value
})

useCrud({ crudExpose, crudOptions })

onMounted(() => {
  crudExpose.doRefresh()
})

onActivated(() => {
  try {
    if (sessionStorage.getItem('pisadmin_rfq_inquiry_dirty') === '1') {
      sessionStorage.removeItem('pisadmin_rfq_inquiry_dirty')
      crudExpose.doRefresh()
    }
  } catch {
    /* ignore */
  }
})
</script>

<style scoped></style>
