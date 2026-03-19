<template>
  <fs-page class="price-template-page">
    <fs-crud ref="crudRef" v-bind="crudBinding" />
  </fs-page>
</template>

<script lang="ts">
import { defineComponent, onMounted, getCurrentInstance } from 'vue'
import { useFs } from '@fast-crud/fast-crud'
import { createCrudOptions } from './crud'

export default defineComponent({
  name: 'CostTemplate',
  setup() {
    const instance = getCurrentInstance()
    const context: any = { componentName: instance?.type.name }
    const { crudBinding, crudRef, crudExpose } = useFs({ createCrudOptions, context })

    onMounted(() => {
      crudExpose.doRefresh()
    })

    return { crudBinding, crudRef }
  }
})
</script>

<style scoped>
.price-template-page :deep(.el-table__fixed-right .cell) {
  white-space: nowrap;
}
</style>
