<template>
  <!--   你的自定义受控组件-->
  <div>
    <el-tag class="many-to-many-tag" :type="randomType" v-for="(item,index) in data" :key="index">{{item}}</el-tag>
  </div>
</template>
<script lang="ts" setup>
import {watch, ref} from "vue";

const props = defineProps({
  modelValue: Array,
  bindValue: Array,
  displayLabel: {
    type:String,
    default: ""
  }
})

// template上使用data
const data = ref()
watch(() => {
      return props.bindValue
    }, // 监听modelValue的变化，
    (value) => {
      const {displayLabel} = props
      const result = value ? value.map((item: any) => {
        return item[displayLabel]
      }) : null
      data.value = result
    }, // 当modelValue值触发后，同步修改data.value的值
    {immediate: true} // 立即触发一次，给data赋值初始值
)

const tagType = ['success', 'info', 'warning', 'danger']
const randomType = (): string => {
  return tagType[Math.floor(Math.random() * tagType.length)];
}
</script>
<style scoped>
.many-to-many-tag{
  margin-right: 5px;
}
.many-to-many-tag:last-child {
  margin-right: 0;
}
</style>
