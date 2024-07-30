<template>
  <div class="table-box">
    <el-container>
      <el-main>
        <el-card>
          <div class="card-header">
            日期选择：
            <div class="block">
              <el-date-picker v-model="user_selection_time" type="date" placeholder="选择日期" size="default"/>
              <el-button type="primary" @click="servers_by_date_search">搜索</el-button>
              <el-button type="primary" @click="servers_by_date_reset">重置</el-button>
            </div>
          </div>
          <br/>
          <el-tabs type="border-card">
            <el-tab-pane label="昨日收入明细">
              <el-table
                  :data="tableData?.yesterday_income"
                  style="width: 100%"
                  :height="tableHeight"
                  row-key="id"
                  lazy
                  :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
              >
                <el-table-column type="index" fixed width="50" label="No."/>
                <el-table-column prop="game" label="游戏名称" min-width="250" show-overflow-tooltip></el-table-column>
                <el-table-column prop="channel" label="渠道" min-width="100" show-overflow-tooltip></el-table-column>
                <el-table-column prop="research_name" label="研发" min-width="100"
                                 show-overflow-tooltip></el-table-column>
                <!--                <el-table-column prop="recharge" label="总流水" min-width="150" sortable-->
                <!--                                 show-overflow-tooltip></el-table-column>-->
                <el-table-column prop="recharge" label="总流水" min-width="150" show-overflow-tooltip></el-table-column>
                <el-table-column prop="discount" label="折扣" min-width="150" show-overflow-tooltip></el-table-column>
                <el-table-column prop="after_folding" label="折后总收入" min-width="150"
                                 show-overflow-tooltip></el-table-column>
                <el-table-column prop="our_folding_income" label="我方折后收入" min-width="150"
                                 show-overflow-tooltip></el-table-column>
                <el-table-column prop="research_folding_income" label="研发折后收入" min-width="150"
                                 show-overflow-tooltip></el-table-column>
                <el-table-column prop="channel_tips" label="渠道备注" show-overflow-tooltip></el-table-column>
                <el-table-column prop="research_tips" label="研发备注" show-overflow-tooltip></el-table-column>
              </el-table>
            </el-tab-pane>
            <el-tab-pane label="前七日收入明细">
              <el-table
                  :data="tableData?.last_week_income"
                  style="width: 100%"
                  :height="tableHeight"
                  row-key="id"
                  lazy
                  :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
              >
                <el-table-column type="index" fixed width="50" label="No."/>
                <el-table-column prop="game" label="游戏名称" min-width="250" show-overflow-tooltip></el-table-column>
                <el-table-column prop="channel" label="渠道" min-width="100" show-overflow-tooltip></el-table-column>
                <el-table-column prop="research_name" label="研发" min-width="100"
                                 show-overflow-tooltip></el-table-column>
                <el-table-column prop="recharge" label="总流水" min-width="150" show-overflow-tooltip></el-table-column>
                <el-table-column prop="discount" label="折扣" min-width="150" show-overflow-tooltip></el-table-column>
                <el-table-column prop="after_folding" label="折后总收入" min-width="150"
                                 show-overflow-tooltip></el-table-column>
                <el-table-column prop="our_folding_income" label="我方折后收入" min-width="150"
                                 show-overflow-tooltip></el-table-column>
                <el-table-column prop="research_folding_income" label="研发折后收入" min-width="150"
                                 show-overflow-tooltip></el-table-column>
                <el-table-column prop="channel_tips" label="渠道备注" show-overflow-tooltip></el-table-column>
                <el-table-column prop="research_tips" label="研发备注" show-overflow-tooltip></el-table-column>
              </el-table>
            </el-tab-pane>
            <el-tab-pane label="前30天收入明细">
              <el-table
                  :data="tableData?.last_month_income"
                  style="width: 100%"
                  :height="tableHeight"
                  row-key="id"
                  lazy
                  :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
              >
                <el-table-column type="index" fixed width="50" label="No."/>
                <el-table-column prop="game" label="游戏名称" min-width="250" show-overflow-tooltip></el-table-column>
                <el-table-column prop="channel" label="渠道" min-width="100" show-overflow-tooltip></el-table-column>
                <el-table-column prop="research_name" label="研发" min-width="100"
                                 show-overflow-tooltip></el-table-column>
                <el-table-column prop="recharge" label="总流水" min-width="150" show-overflow-tooltip></el-table-column>
                <el-table-column prop="discount" label="折扣" min-width="150" show-overflow-tooltip></el-table-column>
                <el-table-column prop="after_folding" label="折后总收入" min-width="150"
                                 show-overflow-tooltip></el-table-column>
                <el-table-column prop="our_folding_income" label="我方折后收入" min-width="150"
                                 show-overflow-tooltip></el-table-column>
                <el-table-column prop="research_folding_income" label="研发折后收入" min-width="150"
                                 show-overflow-tooltip></el-table-column>
                <el-table-column prop="channel_tips" label="渠道备注" show-overflow-tooltip></el-table-column>
                <el-table-column prop="research_tips" label="研发备注" show-overflow-tooltip></el-table-column>
              </el-table>
            </el-tab-pane>
            <el-tab-pane label="上月收入明细">
              <el-table
                  :data="tableData?.current_month_income"
                  style="width: 100%"
                  :height="tableHeight"
                  row-key="id"
                  lazy
                  :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
              >
                <el-table-column type="index" fixed width="50" label="No."/>
                <el-table-column prop="game" label="游戏名称" min-width="250" show-overflow-tooltip></el-table-column>
                <el-table-column prop="channel" label="渠道" min-width="100" show-overflow-tooltip></el-table-column>
                <el-table-column prop="research_name" label="研发" min-width="100"
                                 show-overflow-tooltip></el-table-column>
                <el-table-column prop="recharge" label="总流水" min-width="150" show-overflow-tooltip></el-table-column>
                <el-table-column prop="discount" label="折扣" min-width="150" show-overflow-tooltip></el-table-column>
                <el-table-column prop="after_folding" label="折后总收入" min-width="150"
                                 show-overflow-tooltip></el-table-column>
                <el-table-column prop="our_folding_income" label="我方折后收入" min-width="150"
                                 show-overflow-tooltip></el-table-column>
                <el-table-column prop="research_folding_income" label="研发折后收入" min-width="150"
                                 show-overflow-tooltip></el-table-column>
                <el-table-column prop="channel_tips" label="渠道备注" show-overflow-tooltip></el-table-column>
                <el-table-column prop="research_tips" label="研发备注" show-overflow-tooltip></el-table-column>
              </el-table>
            </el-tab-pane>
            <el-tab-pane label="本月收入明细">
              <el-table
                  :data="tableData?.this_month_income"
                  style="width: 100%"
                  row-key="id"
                  lazy
                  :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
              >
                <el-table-column type="index" fixed width="50" label="No."/>
                <el-table-column prop="game" label="游戏名称" min-width="250" show-overflow-tooltip></el-table-column>
                <el-table-column prop="channel" label="渠道" min-width="100" show-overflow-tooltip></el-table-column>
                <el-table-column prop="research_name" label="研发" min-width="100"
                                 show-overflow-tooltip></el-table-column>
                <el-table-column prop="recharge" label="总流水" min-width="150" show-overflow-tooltip></el-table-column>
                <el-table-column prop="discount" label="折扣" min-width="150" show-overflow-tooltip></el-table-column>
                <el-table-column prop="after_folding" label="折后总收入" min-width="150"
                                 show-overflow-tooltip></el-table-column>
                <el-table-column prop="our_folding_income" label="我方折后收入" min-width="150"
                                 show-overflow-tooltip></el-table-column>
                <el-table-column prop="research_folding_income" label="研发折后收入" min-width="150"
                                 show-overflow-tooltip></el-table-column>
                <el-table-column prop="channel_tips" label="渠道备注" show-overflow-tooltip></el-table-column>
                <el-table-column prop="research_tips" label="研发备注" show-overflow-tooltip></el-table-column>
              </el-table>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script lang="ts" setup>
import {computed, nextTick, onMounted, onUnmounted, ref} from "vue";
import {getIncome} from './crud'

//接口地址

interface Income_detil {
  id: number;
  game: string;
  channel: string;
  recharge: string;
  main_body: string;
  discount: string;
  after_folding: string;
  our_folding_income: string;
  research_folding_income: string;
  channel_tips: string;
  research_tips: string;
  release_date: string;
  research_name: string;
  channel_company: string;
  research_company: string;
  our_ratio: string;
  research_ratio: string;
  slotting_ratio: string;
  our_income: string;
  research_income: string;
  hasChildren?: boolean;
  children?: Income_detil[];
}

interface TableData {
  yesterday_income: Income_detil[];
  last_week_income: Income_detil[];
  last_month_income: Income_detil[];
  current_month_income: Income_detil[];
  this_month_income: Income_detil[];
}

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
const response_data = ref<TableData>({
  yesterday_income: [],
  last_week_income: [],
  last_month_income: [],
  current_month_income: [],
  this_month_income: [],
});
const tableData = ref<TableData>();

// 初始化获取今日数据
onMounted(async () => {
  try {
    const response = await getIncome()
    if (response) {
      response_data.value = response
    } else {
      response_data.value = {
        yesterday_income: [],
        last_week_income: [],
        last_month_income: [],
        current_month_income: [],
        this_month_income: [],
      };
    }
    tableData.value = response_data.value;
  } catch (error) {
    console.error("请求数据失败:", error);
  }
});
const servers_by_date_search = async () => {
  try {
    const response = await getIncome({
      date: formatDate(user_selection_time.value),
    });
    if (response) {
      response_data.value = response
    } else {
      response_data.value = {
        yesterday_income: [],
        last_week_income: [],
        last_month_income: [],
        current_month_income: [],
        this_month_income: [],
      };
    }
    tableData.value = response_data.value;
  } catch (error) {
    console.error("请求数据失败:", error);
  }
};

// 日历重置操作
const servers_by_date_reset = async () => {
  try {
    const response = await getIncome({
      date: formatDate(currentDateTime.value),
    });
    if (response) {
      response_data.value = response
    } else {
      response_data.value = {
        yesterday_income: [],
        last_week_income: [],
        last_month_income: [],
        current_month_income: [],
        this_month_income: [],
      };
    }
    tableData.value = response_data.value;
  } catch (error) {
    console.error("请求数据失败:", error);
  }
};

const tableHeight = ref("500px"); // 表格初始高度，可以根据需要调整

// 设置表格高度
const setTableHeight = () => {
  const screenHeight = window.innerHeight;
  tableHeight.value = `${Math.floor(screenHeight - 325)}px`; // 例如设置为屏幕高度的60%
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
