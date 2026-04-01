<template>
  <div ref="chartRef" class="trend-chart"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import * as echarts from 'echarts';

const props = defineProps<{
  data: Array<{ month: string; count?: number; quotes?: number; won?: number }>;
  type: 'buyer' | 'supplier';
}>();

const chartRef = ref();

function initChart() {
  if (!chartRef.value) return;
  const chart = echarts.init(chartRef.value);

  const xData = props.data.map(d => d.month);

  if (props.type === 'buyer') {
    const yData = props.data.map(d => d.count || 0);
    chart.setOption({
      title: { text: '业务趋势', left: 'left' },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: xData },
      yAxis: { type: 'value' },
      series: [{
        type: 'line',
        data: yData,
        smooth: true,
        areaStyle: { opacity: 0.3 },
      }],
    });
  } else {
    const quotesData = props.data.map(d => d.quotes || 0);
    const wonData = props.data.map(d => d.won || 0);
    chart.setOption({
      title: { text: '报价与中标趋势', left: 'left' },
      tooltip: { trigger: 'axis' },
      legend: { data: ['报价数', '中标数'], right: 0 },
      xAxis: { type: 'category', data: xData },
      yAxis: { type: 'value' },
      series: [
        { name: '报价数', type: 'line', data: quotesData, smooth: true },
        { name: '中标数', type: 'line', data: wonData, smooth: true },
      ],
    });
  }
}

onMounted(initChart);
watch(() => props.data, initChart);
</script>

<style scoped lang="scss">
.trend-chart {
  width: 100%;
  height: 300px;
}
</style>
