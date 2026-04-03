<template>
	<fs-page>
		<fs-crud ref="crudRef" v-bind="crudBinding"> </fs-crud>
		<subDict ref="subDictRef"></subDict>
	</fs-page>
</template>

<script lang="ts" setup name="dictionary">
import { ref, onMounted, defineAsyncComponent } from 'vue';
import { useFs } from '@fast-crud/fast-crud';
import { createCrudOptions } from './crud';
const subDict = defineAsyncComponent(() => import('./subDict/index.vue'));
const subDictRef = ref();

const { crudBinding, crudRef, crudExpose } = useFs({ createCrudOptions, context: { subDictRef } });

// 页面打开后获取列表数据
onMounted(() => {
	crudExpose.doRefresh();
});
</script>
