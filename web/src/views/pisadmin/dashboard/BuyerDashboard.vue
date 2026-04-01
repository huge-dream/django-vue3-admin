<template>
  <div class="buyer-dashboard">
    <div class="header">
      <h2>采购方看板</h2>
      <span class="date">{{ currentDate }}</span>
    </div>

    <!-- KPI Cards -->
    <el-row :gutter="16" class="kpi-row">
      <el-col :span="6">
        <KpiCard
          :value="kpi.total_inquiries"
          label="询价单总数"
          icon="fa fa-file-text-o"
          icon-bg="#e6f7ff"
          icon-color="#1890ff"
        />
      </el-col>
      <el-col :span="6">
        <KpiCard
          :value="kpi.pending_inquiries"
          label="待报价询价单"
          icon="fa fa-clock-o"
          icon-bg="#fff7e6"
          icon-color="#fa8c16"
        />
      </el-col>
      <el-col :span="6">
        <KpiCard
          :value="kpi.completed_quotes"
          label="已完成报价"
          icon="fa fa-check-circle-o"
          icon-bg="#f6ffed"
          icon-color="#52c41a"
        />
      </el-col>
      <el-col :span="6">
        <KpiCard
          :value="kpi.total_suppliers"
          label="供应商总数"
          icon="fa fa-building-o"
          icon-bg="#f9f0ff"
          icon-color="#722ed1"
        />
      </el-col>
    </el-row>

    <!-- Main Content -->
    <el-row :gutter="16" class="main-row">
      <el-col :span="12">
        <el-card title="待办任务">
          <template #header>
            <span>待办任务</span>
          </template>
          <BuyerTaskList :tasks="tasks" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>业务趋势</span>
          </template>
          <TrendChart :data="trend" type="buyer" />
        </el-card>
      </el-col>
    </el-row>

    <!-- Messages -->
    <el-card class="message-card">
      <template #header>
        <span>消息通知</span>
      </template>
      <MessageList :messages="messages" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useDashboardStore } from '/@/stores/modules/dashboard';
import KpiCard from '/@/components/pisadmin/dashboard/KpiCard.vue';
import TrendChart from '/@/components/pisadmin/dashboard/TrendChart.vue';
import MessageList from '/@/components/pisadmin/dashboard/MessageList.vue';
import BuyerTaskList from '/@/components/pisadmin/dashboard/BuyerTaskList.vue';

const store = useDashboardStore();
const { buyer } = storeToRefs(store);

const kpi = computed(() => buyer.value?.kpi || {
  total_inquiries: 0,
  pending_inquiries: 0,
  completed_quotes: 0,
  total_suppliers: 0,
});
const tasks = computed(() => buyer.value?.tasks || []);
const trend = computed(() => buyer.value?.trend || []);
const messages = computed(() => buyer.value?.messages || []);

const currentDate = new Date().toLocaleDateString('zh-CN', {
  year: 'numeric',
  month: 'long',
  day: 'numeric',
});
</script>

<style scoped lang="scss">
.buyer-dashboard {
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    h2 { margin: 0; }
    .date { color: var(--el-text-color-secondary); }
  }
  .kpi-row { margin-bottom: 16px; }
  .main-row { margin-bottom: 16px; }
  .message-card { margin-top: 16px; }
}
</style>
