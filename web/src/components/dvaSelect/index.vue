<template>
  <!--   你的自定义受控组件-->
  <el-select-v2
      v-model="data"
      :options="options"
      style="width: 100%;"
      :clearable="true"
      :props="selectProps"
      @change="onDataChange"

  />
</template>
<script lang="ts" setup>
import {ref, defineComponent, watch, computed, toRefs, toRaw, onMounted} from 'vue'
import {useUi} from "@fast-crud/fast-crud";
import {request} from "/@/utils/service";

const props = defineProps({
  dict: { // 接收来自FastCrud配置中的dict数据
    type: Array,
    required: true,
  },
  modelValue: {}
})
const emit = defineEmits(['update:modelValue'])
// 获取数据
const dataList = ref([])

function getData(params) {
  request({
    url: props.dict.url,
    params: params
  }).then(res => {
    dataList.value = res.data
  })

}

// template上使用data
const data = ref()
// const data = computed({
//   get: () => {
//     console.log("有默认值", props.modelValue)
//     //getData({id:props.modelValue})
//
//     console.log(11, dataList)
//     // const {data} = res
//     // console.log("get",data[0][selectProps.value.label])
//     if (dataList && dataList.length === 1) {
//       return dataList[0][selectProps.value.value]
//     } else {
//       // console.log("aa",res.data)
//       return props.modelValue
//     }
//     // return props.modelValue
//   },
//   set: (val) => {
//     //data.value =  val
//     return val
//   }
// })
const options = ref([])
const selectProps = ref({
  label: 'label',
  value: 'value'
})
watch(
    () => {
      return props.modelValue
    }, // 监听modelValue的变化，
    (value) => {
      // data.value = value
      request({
        url: props.dict.url,
        params: {
          id: props.modelValue
        }
      }).then(res => {
        const dataList = res.data
        console.log(dataList)
        if (dataList && dataList.length === 1) {
          data.value = dataList[0][selectProps.value.label]
        }else{
          data.value = null
        }
      })
    }, // 当modelValue值触发后，同步修改data.value的值
    {immediate: true} // 立即触发一次，给data赋值初始值
)
//获取表单校验上下文
const {ui} = useUi()
const formValidator = ui.formItem.injectFormItemContext();
// 当data需要变化时，上报给父组件
// 父组件监听到update:modelValue事件后，会更新props.modelValue的值
// 然后watch会被触发，修改data.value的值。
function onDataChange(value) {
  emit('update:modelValue', value)
  data.value = value
  //触发校验
  formValidator.onChange()
  formValidator.onBlur()
}


if (props.dict.url instanceof Function) {
  request(props.dict.url).then((res) => {
    options.value = res.data
  })
} else {
  selectProps.value.label = props.dict.label
  selectProps.value.value = props.dict.value
  request({
    url: props.dict.url
  }).then((res) => {
    options.value = res.data
  })
}


// onMounted(() => {
//   getData({id: props.modelValue})
// })

</script>
<style scoped lang="scss">
.el-select .el-input__wrapper .el-input__inner::placeholder {
  //color: #a8abb2;
  color: #0d84ff;
}

.el-select-v2 {
  .el-select-v2__wrapper {
    .el-select-v2__placeholder.is-transparent {
      //color: #a8abb2;
      color: #0d84ff;
    }
  }
}


</style>
