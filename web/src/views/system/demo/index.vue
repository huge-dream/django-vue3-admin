<template>
	<fs-page>
		<fs-crud ref="crudRef" v-bind="crudBinding">
      <template #header-top>
        <div id="myEcharts" v-show="isEcharts" v-resize-ob="handleResize" :style="{width: '100%', height: '300px'}"></div>
      </template>
    </fs-crud>
	</fs-page>
</template>

<script lang="ts" setup name="loginLog">
import { ref, onMounted } from 'vue';
import { useFs } from '@fast-crud/fast-crud';
import { createCrudOptions } from './crud';
import * as echarts from "echarts";
const isEcharts = ref(true)
const { crudBinding, crudRef, crudExpose } = useFs({ createCrudOptions,isEcharts,initChart });
const myEcharts = echarts

function initChart() {
  let chart = myEcharts.init(document.getElementById("myEcharts"), "purple-passion");
  // 在这里请求API,例如:
  /***
   *   request({url:'xxxx'}).then(res=>{
   *     // 把chart.setOption写在这里面
   *
   *   })
   *
   */
  chart.setOption({
    title: {
      text: "2021年各月份销售量（单位：件）",
      left: "center",
    },
    xAxis: {
      type: "category",
      data: [
        "一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"
      ]
    },
    tooltip: {
      trigger: "axis"
    },
    yAxis: {
      type: "value"
    },
    series: [
      {
        data: [
          606, 542, 985, 687, 501, 787, 339, 706, 383, 684, 669, 737
        ],
        type: "line",
        smooth: true,
        itemStyle: {
          normal: {
            label: {
              show: true,
              position: "top",
              formatter: "{c}"
            }
          }
        }
      }
    ]
  });
  window.onresize = function () {
    chart.resize();
  };
}

function handleResize(size) {
  console.log(size)
}

// 页面打开后获取列表数据
onMounted(() => {
	crudExpose.doRefresh();
  initChart()
});
</script>
