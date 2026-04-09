<template>
   <div>
     <fs-crud ref="crudRef" v-bind="crudBinding">
     </fs-crud>
   </div>
</template>

<script setup lang="ts">
import { computed, defineComponent, onMounted, watch } from "vue";
import { useI18n } from "vue-i18n";
import {CreateCrudOptionsProps, CreateCrudOptionsRet, useFs, AddReq,
  compute,
  DelReq,
  dict,
  EditReq,
  UserPageQuery,
  UserPageRes} from "@fast-crud/fast-crud";

const { t } = useI18n();

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
          title: t('message.pages.config.formContent.variableTitle'),
          form:{
            component:{
              placeholder: t('message.pages.config.formContent.titlePlaceholder'),
            },
            rules:[{
              required: true,
              message: t('message.pages.config.validation.titleRequired'),
            }]
          }
        },
        key: {
          title: t('message.pages.config.formContent.variableName'),
          form:{
            component:{
              placeholder: t('message.pages.config.formContent.keyPrefix'),
            },
            rules:[{
              required: true,
              message: t('message.pages.config.validation.keyRequired'),
            }]
          }
        },
        value: {
          title: t('message.pages.config.formContent.variableValue'),
          form:{
            component:{
              placeholder: t('message.pages.config.formContent.variableValue'),
            },
            rules:[{
              required: true,
              message: t('message.pages.config.validation.dictKeyRequired'),
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


//通过导出modelValue, 可以导出已经成为input组件
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
</script>
