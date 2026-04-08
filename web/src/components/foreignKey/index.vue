<template>
  <!--   你的自定义受控组件-->
  <div>
    <el-tag :type="randomType">{{ data }}</el-tag>
  </div>
</template>
<script lang="ts" setup>
import {watch, ref} from "vue";

const props = defineProps({
  modelValue: String || Object,
  displayLabel: {
    type:String,
    default: ""
  }
})

// template上使用data
const data = ref()
watch(() => {
      return props.modelValue
    }, // 监听modelValue的变化，
    (value) => {
      if (typeof value === "string") {
        data.value = value
      } else if (typeof value === "object") {
        const {displayLabel} = props
        data.value = value ? value[displayLabel] : null
      } else {
        data.value = null
      }

    }, // 当modelValue值触发后，同步修改data.value的值
    {immediate: true} // 立即触发一次，给data赋值初始值
)

const tagType = ['success', 'info', 'warning', 'danger']
const randomType = (): string => {
  return tagType[Math.floor(Math.random() * tagType.length)];
}
</script>
