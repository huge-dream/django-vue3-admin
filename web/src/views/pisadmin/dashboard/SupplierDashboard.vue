<template>
  <div class="supplier-dashboard">
    <!-- KPI 指标卡片 -->
    <div class="kpi-section">
      <div class="kpi-card blue">
        <div class="kpi-title">报价单总数</div>
        <div class="kpi-value">{{ kpi.total_quotes.toLocaleString() }}</div>
        <div class="kpi-trend trend-up">
          <i class="fa fa-arrow-up"></i> 较上月 +8%
        </div>
      </div>
      <div class="kpi-card orange">
        <div class="kpi-title">待报价</div>
        <div class="kpi-value">{{ kpi.pending_quotes }}</div>
        <div class="kpi-trend" style="color: #2E5BFF;">等待报价</div>
      </div>
      <div class="kpi-card green">
        <div class="kpi-title">已中标</div>
        <div class="kpi-value">{{ kpi.won_quotes }}</div>
        <div class="kpi-trend trend-up">
          <i class="fa fa-trophy"></i> 中标成功
        </div>
      </div>
      <div class="kpi-card purple">
        <div class="kpi-title">中标率</div>
        <div class="kpi-value">{{ kpi.conversion_rate }}%</div>
        <div class="kpi-trend trend-flat"><i class="fa fa-minus"></i> 持平</div>
      </div>
    </div>

    <!-- 主体内容区 -->
    <div class="main-container">
      <!-- 左侧：待报价清单 -->
      <div class="card task-card">
        <div class="card-header">
          <div class="card-title">
            <i class="fa fa-file-invoice" style="color: #2E5BFF;"></i> 待报价清单
          </div>
          <a href="#" class="view-all">查看全部 <i class="fa fa-arrow-right"></i></a>
        </div>
        <div class="task-table-container">
          <table>
            <thead>
              <tr>
                <th>询价单号</th>
                <th>产品名称</th>
                <th>数量</th>
                <th>截止时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="quote in pendingQuotes" :key="quote.id">
                <td>{{ quote.inquiry_no }}</td>
                <td>{{ quote.item_name || '-' }}</td>
                <td>{{ quote.quantity || '-' }} {{ quote.unit || '' }}</td>
                <td>{{ quote.deadline ? formatDate(quote.deadline) : '-' }}</td>
                <td>
                  <button class="action-btn btn-primary" @click="handleQuote(quote)">
                    去报价
                  </button>
                </td>
              </tr>
              <tr v-if="pendingQuotes.length === 0">
                <td colspan="5" class="empty-cell">暂无待报价清单</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 右侧：消息通知 -->
      <div class="card notification-card">
        <div class="card-header">
          <div class="card-title" style="position: relative;">
            <i class="fa fa-bell" style="color: #2E5BFF;"></i> 消息通知
            <span v-if="unreadCount > 0" class="notif-badge">{{ unreadCount }}</span>
          </div>
          <a href="#" class="view-all">全部消息</a>
        </div>
        <ul class="notification-list">
          <li v-for="msg in messages" :key="msg.id" class="notification-item">
            <div :class="getNotifIconClass(msg.title)">
              <i :class="getNotifIcon(msg.title)"></i>
            </div>
            <div class="notif-content">
              <div class="notif-header">
                <span class="notif-title">{{ msg.title }}</span>
                <span class="notif-time">{{ formatMsgTime(msg.created_at) }}</span>
              </div>
              <p class="notif-desc">{{ msg.content }}</p>
              <a href="#" class="notif-link">查看详情 <i class="fa fa-arrow-right" style="font-size: 10px;"></i></a>
            </div>
          </li>
          <li v-if="messages.length === 0" class="empty-notif">
            暂无消息通知
          </li>
        </ul>
      </div>
    </div>

    <!-- 底部图表区域 -->
    <div class="card chart-section">
      <div class="card-header">
        <div class="card-title">
          <i class="fa fa-chart-line" style="color: #2E5BFF;"></i> 报价与中标趋势
        </div>
        <div class="chart-legend">
          <span><span class="legend-dot" style="background: #2E5BFF;"></span>报价数</span>
          <span><span class="legend-dot" style="background: #10B981;"></span>中标数</span>
        </div>
      </div>
      <div class="chart-container">
        <div ref="chartRef" class="trend-chart"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, watch } from 'vue';
import { storeToRefs } from 'pinia';
import { useDashboardStore } from '/@/stores/modules/dashboard';
import * as echarts from 'echarts';

const store = useDashboardStore();
const { supplier } = storeToRefs(store);

const chartRef = ref();

const kpi = computed(() => supplier.value?.kpi || {
  total_quotes: 0,
  pending_quotes: 0,
  won_quotes: 0,
  conversion_rate: 0,
});
const pendingQuotes = computed(() => supplier.value?.pending_quotes || []);
const trend = computed(() => supplier.value?.trend || []);
const messages = computed(() => supplier.value?.messages || []);

const unreadCount = computed(() => {
  return messages.value.filter(m => !m.is_read).length || 3;
});

function handleQuote(quote: any) {
  console.log('Quote action:', quote);
}

function formatDate(date: string) {
  if (!date) return '';
  const d = new Date(date);
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`;
}

function formatMsgTime(time: string) {
  if (!time) return '';
  const d = new Date(time);
  const now = new Date();
  const diff = now.getTime() - d.getTime();
  const minutes = Math.floor(diff / 60000);
  if (minutes < 60) return `${minutes}分钟前`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}小时前`;
  const days = Math.floor(hours / 24);
  if (days === 1) return '昨天';
  return `${days}天前`;
}

function getNotifIconClass(title: string) {
  if (title?.includes('报价')) return 'notif-icon icon-quote';
  if (title?.includes('中标') || title?.includes('成功')) return 'notif-icon icon-win';
  return 'notif-icon icon-alert';
}

function getNotifIcon(title: string) {
  if (title?.includes('报价')) return 'fa fa-file-invoice-dollar';
  if (title?.includes('中标') || title?.includes('成功')) return 'fa fa-trophy';
  if (title?.includes('资质') || title?.includes('补充')) return 'fa fa-exclamation-triangle';
  return 'fa fa-bell';
}

function initChart() {
  if (!chartRef.value) return;
  const chart = echarts.getInstanceByDom(chartRef.value) || echarts.init(chartRef.value);

  // 使用后端返回的 trend 数据，如果没有则用模拟数据
  let labels: string[] = [];
  let quotesData: number[] = [];
  let wonData: number[] = [];

  if (trend.value && trend.value.length > 0) {
    labels = trend.value.map(d => d.month);
    quotesData = trend.value.map(d => d.quotes || 0);
    wonData = trend.value.map(d => d.won || 0);
  } else {
    // 模拟数据
    const today = new Date();
    for (let i = 5; i >= 0; i--) {
      const d = new Date(today);
      d.setMonth(d.getMonth() - i);
      labels.push(`${d.getFullYear()}-${(d.getMonth() + 1).toString().padStart(2, '0')}`);
    }
    quotesData = [12, 15, 18, 14, 20, 22];
    wonData = [3, 5, 6, 4, 7, 8];
  }

  chart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: labels,
      boundaryGap: false,
      axisLine: { lineStyle: { color: '#E5E7EB' } },
      axisLabel: { color: '#9CA3AF', fontSize: 11 }
    },
    yAxis: [
      {
        type: 'value',
        name: '单据数量',
        min: 0,
        axisLine: { show: false },
        axisLabel: { color: '#9CA3AF', fontSize: 11 },
        splitLine: { lineStyle: { color: '#F3F4F6', type: 'dashed' } }
      }
    ],
    series: [
      {
        name: '报价数',
        type: 'line',
        data: quotesData,
        smooth: true,
        itemStyle: { color: '#2E5BFF' },
        areaStyle: { color: 'rgba(46, 91, 255, 0.05)' },
        lineStyle: { width: 2 },
      },
      {
        name: '中标数',
        type: 'line',
        data: wonData,
        smooth: true,
        itemStyle: { color: '#10B981' },
        areaStyle: { color: 'rgba(16, 185, 129, 0.05)' },
        lineStyle: { width: 2 },
      }
    ]
  });
}

onMounted(() => {
  initChart();
  window.addEventListener('resize', () => chartRef.value && echarts.getInstanceByDom(chartRef.value)?.resize());
});

watch(trend, () => {
  initChart();
});
</script>

<style scoped lang="scss">
.supplier-dashboard {
  --primary-color: #2E5BFF;
  --text-main: #1F2937;
  --text-secondary: #6B7280;
  --bg-body: #F3F4F6;
  --bg-card: #FFFFFF;
  --danger: #EF4444;
  --warning: #F59E0B;
  --success: #10B981;
  --purple: #8B5CF6;
  --border-color: #E5E7EB;
  font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: var(--bg-body);
  padding: 24px;
  border-radius: 0;
  margin: -24px;
  min-height: calc(100vh - 64px);
}

/* KPI 卡片区域 */
.kpi-section {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  margin-bottom: 24px;
}

.kpi-card {
  background: var(--bg-card);
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  border: 1px solid var(--border-color);
  position: relative;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  }

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 4px;
  }

  &.blue::before { background: var(--primary-color); }
  &.green::before { background: var(--success); }
  &.orange::before { background: var(--warning); }
  &.purple::before { background: var(--purple); }
}

.kpi-title {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}

.kpi-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-main);
  margin: 12px 0 8px 0;
  letter-spacing: -0.5px;
}

.kpi-trend {
  font-size: 12px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;

  &.trend-up { color: var(--success); }
  &.trend-flat { color: var(--warning); }
  &.trend-down { color: var(--danger); }
}

/* 主体容器 */
.main-container {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

/* 卡片通用样式 */
.card {
  background: var(--bg-card);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  border: 1px solid var(--border-color);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-main);
  display: flex;
  align-items: center;
  gap: 8px;
}

.view-all {
  font-size: 13px;
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;

  &:hover {
    gap: 8px;
  }
}

/* 待办任务表格 */
.task-table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

th {
  text-align: left;
  padding: 12px 16px;
  background-color: #F9FAFB;
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 13px;
  border-bottom: 1px solid var(--border-color);
}

td {
  padding: 16px;
  border-bottom: 1px solid #F3F4F6;
  color: var(--text-main);
  vertical-align: middle;
}

tr:hover {
  background-color: #F9FAFB;
}

tr:last-child td {
  border-bottom: none;
}

.action-btn {
  padding: 6px 16px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-primary { background-color: var(--primary-color); color: white; }
.btn-primary:hover { background-color: #1d4eff; }

.empty-cell {
  text-align: center;
  color: var(--text-secondary);
  padding: 32px !important;
}

/* 消息通知 */
.notif-badge {
  position: absolute;
  top: -8px;
  right: -12px;
  background: var(--danger);
  color: white;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 10px;
  font-weight: bold;
}

.notification-list {
  list-style: none;
}

.notification-item {
  display: flex;
  gap: 16px;
  padding: 16px 0;
  border-bottom: 1px solid #F3F4F6;

  &:last-child {
    border-bottom: none;
    padding-bottom: 0;
  }

  &:first-child {
    padding-top: 0;
  }

  &:hover {
    background-color: #F9FAFB;
    margin: 0 -16px;
    padding-left: 16px;
    padding-right: 16px;
    border-radius: 8px;
  }
}

.notif-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 18px;
}

.icon-quote { background: #EFF6FF; color: #2563EB; }
.icon-win { background: #ECFDF5; color: #059669; }
.icon-alert { background: #FFFBEB; color: #D97706; }

.notif-content {
  flex: 1;
}

.notif-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 4px;
}

.notif-title {
  font-weight: 600;
  color: var(--text-main);
  font-size: 14px;
}

.notif-time {
  font-size: 12px;
  color: #9CA3AF;
  white-space: nowrap;
}

.notif-desc {
  color: var(--text-secondary);
  font-size: 13px;
  line-height: 1.5;
  margin-bottom: 8px;
}

.notif-link {
  color: var(--primary-color);
  text-decoration: none;
  font-size: 13px;
  font-weight: 500;

  &:hover { text-decoration: underline; }
}

.empty-notif {
  text-align: center;
  color: var(--text-secondary);
  padding: 32px 0;
}

/* 图表区域 */
.chart-section {
  margin-top: 0;
}

.chart-legend {
  font-size: 12px;
  color: var(--text-secondary);
  display: flex;
  gap: 16px;

  span {
    display: flex;
    align-items: center;
    gap: 6px;
  }
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.chart-container {
  position: relative;
  height: 300px;
}

.trend-chart {
  width: 100%;
  height: 100%;
}

/* 响应式 */
@media (max-width: 1200px) {
  .main-container {
    grid-template-columns: 1fr;
  }
  .kpi-section {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .kpi-section {
    grid-template-columns: 1fr;
  }
}
</style>
