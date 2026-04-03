<template>
  <fs-page>
    <fs-crud ref="crudRef" v-bind="crudBinding" />
  </fs-page>
</template>

<script setup lang="ts" name="SupplierMaintenance">
import { ref, onMounted } from 'vue'
import { useCrud, useExpose } from '@fast-crud/fast-crud'
import { createCrudOptions } from './crud'

const crudRef = ref()
const crudBinding = ref()
const { crudExpose } = useExpose({ crudRef, crudBinding })

const { crudOptions } = createCrudOptions({ crudExpose })
useCrud({ crudExpose, crudOptions })

onMounted(() => {
  crudExpose?.doRefresh()
})
</script>

<style scoped></style>
