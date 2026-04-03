<template>
  <fs-page class="rfs-operation-logs-page">
    <fs-crud ref="crudRef" v-bind="crudBinding" />
  </fs-page>
</template>

<script setup lang="ts" name="RfsOperationLogs">
import { onMounted, ref } from 'vue'
import { useCrud, useExpose } from '@fast-crud/fast-crud'
import { createCrudOptions } from './crud'

const crudRef = ref()
const crudBinding = ref()
const { crudExpose } = useExpose({ crudRef, crudBinding })

const { crudOptions } = createCrudOptions({ crudExpose, context: {} })
useCrud({ crudExpose, crudOptions })

onMounted(() => {
  crudExpose?.doRefresh?.()
})
</script>

<style scoped>
/* 与参考稿「操作履历明细表」表头风格接近 */
.rfs-operation-logs-page :deep(.el-table__header th) {
  background: var(--el-fill-color-light);
  color: var(--el-text-color-regular);
  font-weight: 600;
}
</style>
