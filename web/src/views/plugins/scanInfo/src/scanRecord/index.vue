<template>
	<fs-page>
		<fs-crud ref="crudRef" v-bind="crudBinding"> </fs-crud>
	</fs-page>
</template>

<script lang="ts" setup name="scanRecord">
import { onMounted } from 'vue';
import { useFs } from '@fast-crud/fast-crud';
import { createCrudOptions } from './crud';
import { handleColumnPermission } from '/@/utils/columnPermission';

const { crudBinding, crudRef, crudExpose, crudOptions, resetCrudOptions } = useFs({ createCrudOptions });

// 页面打开后获取列表数据
onMounted(async () => {
	// 刷新
	crudExpose.doRefresh();
});
</script>
