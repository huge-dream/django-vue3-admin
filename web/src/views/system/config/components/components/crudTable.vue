<template>
   <div>
     <fs-crud ref="crudRef" v-bind="crudBinding">
     </fs-crud>
   </div>
</template>

<script setup lang="ts">
import {computed, defineComponent, onMounted, watch} from "vue";
import {CreateCrudOptionsProps, CreateCrudOptionsRet, useFs, AddReq,
  compute,
  DelReq,
  dict,
  EditReq,
  UserPageQuery,
  UserPageRes} from "@fast-crud/fast-crud";
const createCrudOptions = function ({ crudExpose, context }: CreateCrudOptionsProps): CreateCrudOptionsRet {
  return {
    crudOptions: {
      mode: {
        name: "local",
        isMergeWhenUpdate: true,
        isAppendWhenAdd: true
      },
      actionbar: { buttons: { add: { show: true }, addRow: { show: false } } },
      editable: {
        enabled: true,
        mode: "row",
        activeDefault:true
      },
      form:{
        wrapper:{
          width:"500px"
        },
        col:{
          span:24
        },
        afterSubmit({mode}){
          emit('update:modelValue', crudBinding.value.data);
        }
      },
      toolbar:{
        show:false
      },
      search: {
        disabled: true,
        show: false
      },
      pagination: {
        show: false
      },
      columns: {
        title: {
          title: "标题",
          form:{
            component:{
              placeholder:"请输入标题"
            },
            rules:[{
              required: true,
              message: '必须填写',
            }]
          }
        },
        key: {
          title: "键名",
          form:{
            component:{
              placeholder:"请输入键名"
            },
            rules:[{
              required: true,
              message: '必须填写',
            }]
          }
        },
        value: {
          title: "键值",
          form:{
            component:{
              placeholder:"请输入键值"
            },
            rules:[{
              required: true,
              message: '必须填写',
            }]
          }
        }
      }
    }
  };
}
const { crudBinding, crudRef, crudExpose } = useFs({ createCrudOptions });
const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  }
})
const emit = defineEmits(['update:modelValue'])


//通过导出modelValue, 可以导出成为一个input组件
watch(
    () => {
      return props.modelValue;
    },
    (value = []) => {
      crudBinding.value.data = value;
    },
    {
      immediate: true
    }
);

// 页面打开后获取列表数据
// onMounted(() => {
//   crudExpose.doRefresh();
//   // crudExpose.setTableData([])
//   // crudExpose.editable.enable();
// });
</script>
