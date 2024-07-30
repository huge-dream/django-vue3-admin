<template>
  <div class="table-box">
    <el-container>
      <el-main>
        <el-card>
          <div class="card-header">
            选择日期：
            <div class="block">
              <el-date-picker v-model="user_selection_time" type="date" placeholder="选择日期" size="default"/>
              <el-button type="primary" @click="servers_by_date_search">搜索</el-button>
              <el-button type="primary" @click="servers_by_date_reset">重置</el-button>
<!--              <el-button type="primary" @click="manual_update">手动更新</el-button>-->
            </div>
          </div>
          <br/>
          <el-tabs type="border-card">
            <el-tab-pane label="参考收入">
              <el-table
                  :data="income"
                  style="width: 100%"
                  :height="tableHeight"
                  :default-sort="{ prop: '前一日充值', order: 'descending' }"
                  show-summary
                  :summary-method="getIncomeSummary"
              >
                <el-table-column type="index" fixed width="100" label="No."/>
                <el-table-column prop="游戏名称" label="游戏名称" fixed sortable align="center"
                                 show-overflow-tooltip/>
                <el-table-column prop="前一日充值" label="前一日充值" sortable align="center"/>
                <el-table-column prop="前七日内充值" label="前七日内充值" sortable align="center"/>
                <el-table-column prop="前三十日内充值" label="前三十日内充值" sortable align="center"/>
                <el-table-column prop="上月总充值" label="上月总充值" sortable align="center"/>
                <el-table-column prop="昨日活跃用户（人）" label="昨日活跃用户（人）" sortable align="center"/>
                <el-table-column prop="上线天数" label="上线天数" sortable align="center" width="150"/>
              </el-table>
            </el-tab-pane>
            <el-tab-pane label="版号">
              <el-table :data="banhao" style="width: 100%" :height="tableHeight"
                        :default-sort="{ prop: '前一日总充值', order: 'descending' }">
                <el-table-column type="index" fixed width="100" label="No."/>
                <el-table-column prop="版号" label="版号" sortable fixed align="center"
                                 show-overflow-tooltip/>
                <el-table-column prop="前一日总充值" label="前一日总充值" sortable align="center"/>
                <el-table-column prop="前七日内总充值" label="前七日内总充值" sortable align="center"/>
                <el-table-column prop="前三十日内总充值" label="前三十日内总充值" sortable align="center"/>
                <el-table-column prop="昨日活跃总用户（人）" label="昨日活跃总用户（人）" sortable align="center"/>
              </el-table>
            </el-tab-pane>
            <el-tab-pane label="服务器">
              <el-table :data="instance" style="width: 100%" :height="tableHeight">
                <el-table-column type="index" fixed width="100" label="No."/>
                <el-table-column prop="实例名称" label="实例名称" fixed align="center" min-width="150"/>
                <el-table-column prop="实例ID" label="实例ID" align="center" min-width="150"
                                 show-overflow-tooltip/>
                <el-table-column prop="状态" label="状态" sortable align="center"/>
                <el-table-column prop="CPU" label="CPU" sortable align="center" width="100"/>
                <el-table-column prop="内存" label="内存" sortable align="center" width="100"/>
                <el-table-column prop="主IPv4地址" label="主IPv4地址" sortable align="center"/>
                <!--                <el-table-column prop="次IPv4地址" label="次IPv4地址" sortable align="center"/>-->
                <el-table-column prop="到期时间" label="到期时间" sortable align="center" width="200"/>
                <el-table-column prop="所属账号" label="所属账号" sortable align="center" width="120"/>
              </el-table>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script lang="ts" setup>
import {ref, onMounted, onUnmounted, computed, nextTick} from "vue";
import { request } from '/@/utils/service';
//接口地址
const url = "https://gamemanageapi.jingtanggame.com/api/reportdata/get_report/";
onMounted(() => {
  // 动态设置表格高度
  nextTick(() => {
    setTableHeight();
    window.addEventListener("resize", setTableHeight);
  });
});
onUnmounted(() => {
  // 移除窗口大小变化的监听器
  window.removeEventListener("resize", setTableHeight);
});

// 方法：将日期转换为 YYYY-MM-DD 格式的字符串
function formatDate(date: Date | string | number) {
  if (!date) return "";
  const d = new Date(date);
  const year = d.getFullYear();
  const month = `${d.getMonth() + 1}`.padStart(2, "0");
  const day = `${d.getDate()}`.padStart(2, "0");
  return `${year}-${month}-${day}`;
}

// 计算属性：获取当前日期并格式化为 YYYY-MM-DD
const currentDateTime = computed(() => {
  const now = new Date();
  return formatDate(now);
});

const user_selection_time = ref("");

// 初始化获取今日数据
onMounted(async () => {
  try {
    const response = await request({
      url: url,
      method: "get",
    });
    if (response) {
      banhao.value = response.banhao;
      income.value = response.income;
      instance.value = response.instance;
    } else {
      banhao.value = [];
      income.value = [];
      instance.value = [];
    }
  } catch (error) {
    console.error("请求数据失败:", error);
  }
});
let banhao = ref([]);
let income = ref([]);
let instance = ref([]);
const servers_by_date_search = async () => {
  try {
    const response = await request({
      url: url,
      method: "post",
      data: {
        date: formatDate(user_selection_time.value),
      },
    });

    if (response) {
      banhao.value = response.banhao;
      income.value = response.income;
      instance.value = response.instance;
    } else {
      banhao.value = [];
      income.value = [];
      instance.value = [];
    }

  } catch (error) {
    console.error("请求数据失败:", error);
  }
};

// 日历重置操作
const servers_by_date_reset = async () => {
  try {
    const response = await request({
      url: url,
      method: "post",
      data: {
        date: formatDate(currentDateTime.value),
      },
    });

    if (response) {
      banhao.value = response.banhao;
      income.value = response.income;
      instance.value = response.instance;
    } else {
      banhao.value = [];
      income.value = [];
      instance.value = [];
    }
  } catch (error) {
    console.error("请求数据失败:", error);
  }
};

//手动更新按钮
// const manual_update = async () => {
//   try {
//     const response = await axios.get("https://gamemanageapi.jingtanggame.com/api/manual_update/");
//     if (response.data.error) {
//       ElMessage(
//           {
//             message: response.data.error,
//             type: "error",
//           }
//       );
//     } else {
//       ElMessage(
//           {
//             message: response.data.message,
//             type: "success",
//           }
//       );
//     }
//   } catch (error) {
//     ElMessage(
//         {
//           message: "请求数据失败",
//           type: "error",
//         }
//     );
//   }
// };

const tableHeight = ref("500px"); // 表格初始高度，可以根据需要调整

// 设置表格高度
const setTableHeight = () => {
  const screenHeight = window.innerHeight;
  tableHeight.value = `${Math.floor(screenHeight - 325)}px`; // 例如设置为屏幕高度的60%
};

const getIncomeSummary = (param: { columns: any; data: any }) => {
  const {columns, data} = param;
  const sums: any[] = [];
  columns.forEach((column: any, index: number) => {
    if (index === 0) {
      sums[index] = '合计';
      return;
    }
    if (['上线天数'].includes(column.property)) {
      sums[index] = ''; // 不需要合计的数据列
      return;
    }
    const values = data.map((item: any) => Number(item[column.property]));
    if (!values.every((value: any) => isNaN(value))) {
      sums[index] = values.reduce((prev: any, curr: any) => {
        const value = Number(curr);
        if (!isNaN(value)) {
          return prev + curr;
        } else {
          return prev;
        }
      }, 0);
      sums[index] = sums[index].toFixed(2); // 保留两位小数
    } else {
      sums[index] = '';
    }
  });
  return sums;
};

</script>

<style scoped>
.card-header {
  display: flex;
  align-items: center;
}

.demo-date-picker .block:last-child {
  border-right: none;
}

.title h2 {
  text-align: center;
}

.card-header .block {
  display: flex;
  align-items: center;
  gap: 10px;
}
</style>
