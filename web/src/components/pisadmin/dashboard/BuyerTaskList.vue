<template>
  <el-table :data="tasks" stripe style="width: 100%">
    <el-table-column prop="inquiry_no" label="询价单号" width="120" />
    <el-table-column prop="title" label="标题" />
    <el-table-column prop="status" label="状态" width="100">
      <template #default="{ row }">
        <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
      </template>
    </el-table-column>
    <el-table-column prop="created_at" label="创建时间" width="180">
      <template #default="{ row }">
        {{ formatDate(row.created_at) }}
      </template>
    </el-table-column>
  </el-table>
</template>

<script setup lang="ts">
defineProps<{
  tasks: Array<{
    id: number;
    title: string;
    inquiry_no: string;
    status: string;
    created_at: string;
  }>;
}>();

function getStatusType(status: string) {
  const map: Record<string, string> = {
    '开立': 'info',
    '确认': 'warning',
    '发布': 'primary',
    '报价中': 'success',
  };
  return map[status] || 'info';
}

function formatDate(date: string) {
  if (!date) return '';
  return new Date(date).toLocaleString();
}
</script>
