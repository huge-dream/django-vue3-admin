<template>
  <el-table :data="quotes" stripe style="width: 100%">
    <el-table-column prop="inquiry_no" label="询价单号" width="120" />
    <el-table-column prop="item_name" label="产品名称" />
    <el-table-column prop="quantity" label="数量" width="80" />
    <el-table-column prop="unit" label="单位" width="80" />
    <el-table-column prop="deadline" label="报价截止时间" width="180">
      <template #default="{ row }">
        {{ formatDate(row.deadline) }}
      </template>
    </el-table-column>
    <el-table-column label="操作" width="100" fixed="right">
      <template #default="{ row }">
        <el-button type="primary" link @click="$emit('quote', row)">去报价</el-button>
      </template>
    </el-table-column>
  </el-table>
</template>

<script setup lang="ts">
defineProps<{
  quotes: Array<{
    id: number;
    inquiry_no: string;
    item_name: string;
    quantity: number;
    unit: string;
    deadline: string;
  }>;
}>();

defineEmits(['quote']);

function formatDate(date: string) {
  if (!date) return '';
  return new Date(date).toLocaleString();
}
</script>
