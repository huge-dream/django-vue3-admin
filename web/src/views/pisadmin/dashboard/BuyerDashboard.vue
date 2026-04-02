<template>
  <div class="buyer-dashboard">
    <!-- KPI 指标卡片 -->
    <div class="kpi-section">
      <div class="kpi-card blue">
        <div class="kpi-title">已完成询价单总数</div>
        <div class="kpi-value">{{ kpi.total_inquiries.toLocaleString() }}</div>
        <div class="kpi-trend trend-up">
          <i class="fa fa-arrow-up"></i> 较上月 +12%
        </div>
      </div>
      <div class="kpi-card green">
        <div class="kpi-title">进行中询价单</div>
        <div class="kpi-value">{{ kpi.pending_inquiries }}</div>
        <div class="kpi-trend" style="color: #2E5BFF;">正常流转中</div>
      </div>
      <div class="kpi-card orange">
        <div class="kpi-title">供应商报价及时率</div>
        <div class="kpi-value">92%</div>
        <div class="kpi-trend trend-flat"><i class="fa fa-minus"></i> 持平</div>
      </div>
      <div class="kpi-card red">
        <div class="kpi-title">我的待办任务</div>
        <div class="kpi-value" style="color: #EF4444;">{{ tasks.length }}</div>
        <div class="kpi-trend trend-down">
          <i class="fa fa-exclamation-circle"></i> {{ urgentTasks }}项紧急
        </div>
      </div>
    </div>

    <!-- 主体内容区 -->
    <div class="main-container">
      <!-- 左侧：待办任务 -->
      <div class="card task-card">
        <div class="card-header">
          <div class="card-title">
            <i class="fa fa-tasks" style="color: #2E5BFF;"></i> 我的待办任务
          </div>
          <a href="#" class="view-all">查看全部 <i class="fa fa-arrow-right"></i></a>
        </div>
        <div class="task-table-container">
          <table>
            <thead>
              <tr>
                <th>询价单号</th>
                <th>物料名称</th>
                <th>当前状态</th>
                <th>截止时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="task in tasks" :key="task.id">
                <td>{{ task.inquiry_no }}</td>
                <td>{{ task.title }}</td>
                <td>
                  <span :class="getStatusClass(task.status)">{{ task.status }}</span>
                </td>
                <td>{{ task.created_at ? formatDate(task.created_at) : '-' }}</td>
                <td>
                  <button class="action-btn btn-primary" @click="handleAction(task)">
                    {{ getActionText(task.status) }}
                  </button>
                </td>
              </tr>
              <tr v-if="tasks.length === 0">
                <td colspan="5" class="empty-cell">暂无待办任务</td>
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
          <i class="fa fa-chart-line" style="color: #2E5BFF;"></i> 近30天业务趋势
        </div>
        <div class="chart-legend">
          <span><span class="legend-dot" style="background: #2E5BFF;"></span>发布询价</span>
          <span><span class="legend-dot" style="background: #10B981;"></span>收到报价</span>
          <span><span class="legend-dot" style="background: #F59E0B;"></span>响应率</span>
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
const { buyer } = storeToRefs(store);

const chartRef = ref();

const kpi = computed(() => buyer.value?.kpi || {
  total_inquiries: 0,
  pending_inquiries: 0,
  completed_quotes: 0,
  total_suppliers: 0,
});
const tasks = computed(() => buyer.value?.tasks || []);
const trend = computed(() => buyer.value?.trend || []);
const messages = computed(() => buyer.value?.messages || []);

const urgentTasks = computed(() => {
  return tasks.value.filter(t => t.status?.includes('紧急')).length || 2;
});

const unreadCount = computed(() => {
  return messages.value.filter(m => !m.is_read).length || 3;
});

function getStatusClass(status: string) {
  if (status?.includes('比价') || status?.includes('发布')) return 'status-badge status-blue';
  if (status?.includes('议价') || status?.includes('紧急')) return 'status-badge status-pink';
  return 'status-badge status-gray';
}

function getActionText(status: string) {
  if (status?.includes('比价')) return '去比价';
  if (status?.includes('议价')) return '去议价';
  return '查看详情';
}

function handleAction(task: any) {
  console.log('Action for task:', task);
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

  // 生成近30天的模拟数据
  const labels = [];
  const dataPublish = [2, 3, 2, 4, 3, 5, 4, 3, 5, 6, 4, 3, 4, 5, 7, 6, 5, 4, 3, 4, 5, 6, 5, 4, 3, 4, 5, 4, 3, 4];
  const dataReceive = [1, 2, 1, 3, 2, 4, 3, 2, 4, 5, 3, 2, 3, 4, 6, 5, 4, 3, 2, 3, 4, 5, 4, 3, 2, 3, 4, 3, 2, 3];
  const dataRate = [50, 66, 50, 75, 66, 80, 75, 66, 80, 83, 75, 66, 75, 80, 85, 83, 80, 75, 66, 75, 80, 83, 80, 75, 66, 75, 80, 75, 66, 75];

  const today = new Date();
  for (let i = 29; i >= 0; i--) {
    const d = new Date(today);
    d.setDate(d.getDate() - i);
    labels.push(`${d.getMonth() + 1}/${d.getDate()}`);
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
      },
      {
        type: 'value',
        name: '响应率(%)',
        min: 0,
        max: 100,
        axisLine: { show: false },
        axisLabel: { color: '#9CA3AF', fontSize: 11, formatter: '{value}%' },
        splitLine: { show: false }
      }
    ],
    series: [
      {
        name: '发布询价单',
        type: 'line',
        data: dataPublish,
        smooth: true,
        itemStyle: { color: '#2E5BFF' },
        areaStyle: { color: 'rgba(46, 91, 255, 0.05)' },
        lineStyle: { width: 2 },
        yAxisIndex: 0
      },
      {
        name: '收到报价单',
        type: 'line',
        data: dataReceive,
        smooth: true,
        itemStyle: { color: '#10B981' },
        areaStyle: { color: 'rgba(16, 185, 129, 0.05)' },
        lineStyle: { width: 2 },
        yAxisIndex: 0
      },
      {
        name: '响应率(%)',
        type: 'line',
        data: dataRate,
        smooth: true,
        itemStyle: { color: '#F59E0B' },
        lineStyle: { width: 2, type: 'dashed' },
        yAxisIndex: 1
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
.buyer-dashboard {
  --primary-color: #2E5BFF;
  --text-main: #1F2937;
  --text-secondary: #6B7280;
  --bg-body: #F3F4F6;
  --bg-card: #FFFFFF;
  --danger: #EF4444;
  --warning: #F59E0B;
  --success: #10B981;
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
  &.red::before { background: var(--danger); }
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

.status-badge {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  display: inline-block;
}

.status-blue { background-color: #EFF6FF; color: #2563EB; border: 1px solid #DBEAFE; }
.status-pink { background-color: #FEF2F2; color: #DC2626; border: 1px solid #FECACA; }
.status-gray { background-color: #F3F4F6; color: #4B5563; border: 1px solid #D1D5DB; }

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
