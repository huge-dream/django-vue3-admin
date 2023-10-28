<template>
  <fs-page>
    <fs-crud ref="crudRef" v-bind="crudBinding">

    </fs-crud>
    <fs-form-wrapper ref="addChildrenRef" />
  </fs-page>
</template>

<script lang="ts" setup>
import {ref, onMounted, reactive, computed} from "vue";
import createCrudOptions from "./crud";
import {useExpose, useCrud, useCompute} from "@fast-crud/fast-crud";
import {AddObj} from "./api";
import {ElMessage } from "element-plus"



// crud组件的ref
const crudRef = ref();
// crud 配置的ref
const crudBinding = ref();
// 暴露的方法
const { crudExpose } = useExpose({ crudRef, crudBinding });




// 你的crud配置
const { crudOptions } = createCrudOptions({ crudExpose });
// 初始化crud配置
// eslint-disable-next-line @typescript-eslint/no-unused-vars,no-unused-vars
const { resetCrudOptions } = useCrud({ crudExpose, crudOptions });
// 你可以调用此方法，重新初始化crud配置
// resetCrudOptions(options)

// 页面打开后获取列表数据
onMounted(() => {
  crudExpose.doRefresh();
});
</script>
