<template>
  <div class="supplier-dashboard">
    <div class="header">
      <h2>供应商看板</h2>
      <span class="date">{{ currentDate }}</span>
    </div>

    <!-- KPI Cards -->
    <el-row :gutter="16" class="kpi-row">
      <el-col :span="6">
        <KpiCard
          :value="kpi.total_quotes"
          label="报价单总数"
          icon="fa fa-file-text-o"
          icon-bg="#e6f7ff"
          icon-color="#1890ff"
        />
      </el-col>
      <el-col :span="6">
        <KpiCard
          :value="kpi.pending_quotes"
          label="待报价"
          icon="fa fa-clock-o"
          icon-bg="#fff7e6"
          icon-color="#fa8c16"
        />
      </el-col>
      <el-col :span="6">
        <KpiCard
          :value="kpi.won_quotes"
          label="已中标"
          icon="fa fa-trophy"
          icon-bg="#f6ffed"
          icon-color="#52c41a"
        />
      </el-col>
      <el-col :span="6">
        <KpiCard
          :value="kpi.conversion_rate + '%'"
          label="中标率"
          icon="fa fa-percent"
          icon-bg="#f9f0ff"
          icon-color="#722ed1"
        />
      </el-col>
    </el-row>

    <!-- Main Content -->
    <el-row :gutter="16" class="main-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>待报价清单</span>
          </template>
          <SupplierQuoteList :quotes="pendingQuotes" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>报价与中标趋势</span>
          </template>
          <TrendChart :data="trend" type="supplier" />
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
import SupplierQuoteList from '/@/components/pisadmin/dashboard/SupplierQuoteList.vue';

const store = useDashboardStore();
const { supplier } = storeToRefs(store);

const kpi = computed(() => supplier.value?.kpi || {
  total_quotes: 0,
  pending_quotes: 0,
  won_quotes: 0,
  conversion_rate: 0,
});
const pendingQuotes = computed(() => supplier.value?.pending_quotes || []);
const trend = computed(() => supplier.value?.trend || []);
const messages = computed(() => supplier.value?.messages || []);

const currentDate = new Date().toLocaleDateString('zh-CN', {
  year: 'numeric',
  month: 'long',
  day: 'numeric',
});
</script>

<style scoped lang="scss">
.supplier-dashboard {
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
