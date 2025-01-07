<script setup lang="ts">
import { onMounted, ref, reactive, markRaw } from 'vue';
import dayjs from 'dayjs'
import { ElMessageBox, ElMessage } from 'element-plus';
import { request } from '/@/utils/service';
import { getBaseURL } from '/@/utils/baseUrl';
import type { Action } from 'element-plus'
import { Edit, Refresh } from '@element-plus/icons-vue'
import { copyFileSync, writeFile, writeFileSync } from 'fs';
import { utils, write } from 'xlsx';
import * as echarts from 'echarts';
import { maxBy } from 'lodash';
import { info } from 'console';

const Selectedtitle = ref('')
const OTtasklist = ref([])
const currentTask = ref('')
const options = [
  '课题组1',
  '课题组2',
  '课题组3',
  '课题组4',
]
const value = ref('课题组1')

const fetchAllTaskList = async () => {
  try {
    const response = await request({
      url: 'api/system/task/task_list_all/',
      method: 'get',
    })
    if (response.code == 2000) {
      // 去掉task_type=1的
      OTtasklist.value = response.data.filter(item => item.task_type !== 1)
    }
  } catch (error) {
    console.error(error)
  }
}

const ObTask = (value) => {
  currentTask.value = value
}
const form = reactive({
        name: '',
        description: '',
        options: ['配置项1', '配置项2', '配置项3', '配置项4', '配置项5']
      })
onMounted(() => {
  fetchAllTaskList()
})
</script>

<template>
  <div>
    <div class="container">
      <div class="OTheader">
        <el-select v-model="Selectedtitle" placeholder="选择课题组" size="large" class="select-group">
          <el-option
            v-for="item in OTtasklist"
            :key="item.task_name"
            :value="item.task_name"
            @click="ObTask(item.task_id)"
          />
        </el-select>
      </div>
      <div class="ContentBody" v-if="true">
        <h1 class="title">
          课题组评价配置
        </h1>
        <el-segmented class="segment" v-model="value" :options="options" block>
          <template #default="{ item }">
            <div class="segment-item">{{ item }}</div>
          </template>
        </el-segmented>
        <div v-for="item in options" :key="item">
          <div class="evacontent" v-if="item == value">
            <span class="text-xl text-center text-gray-700 bg-clip-text"></span>
            <div >
                <el-form ref="form" :model="form" label-width="120px">
                    <el-form-item label="课题组名称">
                    <el-input v-model="form.name"></el-input>
                    </el-form-item>
                    <el-form-item label="课题描述">
                    <el-input type="textarea" v-model="form.description"></el-input>
                    </el-form-item>
                    <el-form-item label="配置项">
                        <div v-for="item in form.options" :key="item.id" class="wightFillblock">
                            <el-input v-model="item.value" placeholder="请输入配置值"></el-input>
                        </div>
                    </el-form-item>
                    <el-form-item>
                    <el-button type="primary" @click="submitForm">提交</el-button>
                    <el-button @click="resetForm">重置</el-button>
                    </el-form-item>
                </el-form>
            </div>
            <div class="submitbutton">
              <el-button type="primary">生成课题组</el-button>
            </div>
          </div>
        </div>
      </div>
      <div class="ContentBody" v-else>
        <el-empty description="请选择进行配置" />
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.container {
  margin: 30px;
  padding: 20px;
  min-height: 650px;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.3s ease;
}

.container:hover {
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

.OTheader {
  margin-bottom: 20px;
}

.select-group {
  width: 100%;
  max-width: 340px;
}

.ContentBody {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.title {
  font-size: 2rem;
  font-weight: 800;
  text-align: center;
  color: #4a4a4a;
  margin-bottom: 20px;
}

.segment {
  margin-top: 20px;
  background-color: #dadada;
}

.segment-item {
  font-size: 1rem;
  font-weight: bold;
  text-align: center;
}

.evacontent {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.wightFillblock {
  display: flex;
  align-items: center;
  background-color: #ffffff;
  border-radius: 10px;
  border: 1px solid #cccccc;
  width: 600px;
  height: 50px;
  margin: 10px;
  padding: 10px;
}

.submitbutton {
  width: 80%;
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>