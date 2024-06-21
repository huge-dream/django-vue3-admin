<template>
    <fs-page>
        <fs-crud ref="crudRef" v-bind="crudBinding"> </fs-crud>
    </fs-page>
</template>

<script lang="ts" setup>
import { ref, onMounted, watch } from 'vue';
import { useFs } from '@fast-crud/fast-crud';
import { createCrudOptions } from './crud';


const props = defineProps<{
    taskItem: object;
}>();


const { crudBinding, crudRef, crudExpose } = useFs({ createCrudOptions, context: { taskItem: props.taskItem } });
// 页面打开后获取列表数据
onMounted(() => {
    crudExpose.doRefresh();
});
</script>
