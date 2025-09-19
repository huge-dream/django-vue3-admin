<template>
	<div class="upgrade-dialog">
		<el-dialog
			v-model="isShow"
			width="500px"
			destroy-on-close
			:show-close="true"
			:close-on-click-modal="false"
			:close-on-press-escape="false"
		>
      <div style="text-align: center">
        <div v-if="status===0">
          <el-icon size="100" color="rgb(177, 179, 184)"><Loading /></el-icon>
          <div style="font-size: 18px">识别中请稍等</div>
        </div>
        <div v-if="status===1">
          <el-icon size="100" color="#57B046"><CircleCheckFilled /></el-icon>
          <div style="font-size: 18px">扫码成功</div>
        </div>
        <div v-if="status===2">
          <el-icon size="100" color="#F56C6C"><CircleCloseFilled /></el-icon>
          <div style="font-size: 18px">条码重复</div>
        </div>
        <div v-if="status===3">
          <el-icon size="100" color="#F56C6C"><WarningFilled /></el-icon>
          <div style="font-size: 18px">条码错误</div>
        </div>
        <div style="font-size: 16px;color: #979b9c">{{scanCode}}</div>
        <div style="width: 100%;margin-top: 50px;">
          <el-button type="primary" style="width: 300px;" size="large" @click="onclick" v-if="time !== -1">{{time}}秒后自动关闭</el-button>
          <el-button type="primary" style="width: 300px;" size="large" @click="onclick" v-else>关闭</el-button>
        </div>
      </div>
		</el-dialog>
	</div>
</template>

<script setup lang="ts" name="layoutUpgrade">
import {reactive, computed, onMounted, ref} from 'vue';
import * as api from './api';
import mittBus from "/@/utils/mitt";
const isShow = ref(false);
const scanCode = ref('');
const status = ref(0);
const time = ref(-1)
const timer = ref()

const postData = () => {
  api.AddObj({
    code: scanCode.value,
  }).then(() => {
    time.value = 5;
    status.value = 1;
    timer.value = setInterval(() => {
      if (time.value <= 0){
        onclick()
        clearTimeout(timer.value)
        time.value = 5
      } else {
        time.value -= 1
      }
    }, 1000)
  }).catch((err: any) => {
    status.value = err?.msg === '重复扫码' ? 2 : 3
    time.value = -1
  })
}
const onclick = () => {
  isShow.value = false;
  mittBus.emit('scanDataDoRefresh', () => {});
}
// 页面加载时
onMounted(() => {

});
// 暴露变量
defineExpose({
	isShow,
	onclick,
	scanCode,
  postData
});
</script>

<style scoped lang="scss">

</style>
