<template>
  <el-card class="kpi-card" shadow="hover">
    <div class="kpi-content">
      <div class="kpi-icon" :style="{ background: iconBg }">
        <i :class="icon" :style="{ color: iconColor }"></i>
      </div>
      <div class="kpi-info">
        <div class="kpi-value">{{ value }}</div>
        <div class="kpi-label">{{ label }}</div>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
defineProps<{
  value: number | string;
  label: string;
  icon: string;
  iconBg?: string;
  iconColor?: string;
}>();
</script>

<style scoped lang="scss">
.kpi-card {
  border-radius: 12px;
  .kpi-content {
    display: flex;
    align-items: center;
    gap: 16px;
  }
  .kpi-icon {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    i {
      font-size: 28px;
    }
  }
  .kpi-info {
    .kpi-value {
      font-size: 28px;
      font-weight: 700;
      color: var(--el-text-color-primary);
    }
    .kpi-label {
      font-size: 14px;
      color: var(--el-text-color-secondary);
      margin-top: 4px;
    }
  }
}
</style>
