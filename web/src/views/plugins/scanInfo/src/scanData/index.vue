<template>
	<fs-page>
		<fs-crud ref="crudRef" v-bind="crudBinding"> </fs-crud>
	</fs-page>
</template>

<script lang="ts" setup name="scanData">
import { onMounted,onUnmounted } from 'vue';
import { useFs } from '@fast-crud/fast-crud';
import { createCrudOptions } from './crud';
import mittBus from "/@/utils/mitt";
import { handleColumnPermission } from '/@/utils/columnPermission';

const { crudBinding, crudRef, crudExpose, crudOptions, resetCrudOptions } = useFs({ createCrudOptions });

// 页面打开后获取列表数据
onMounted(async () => {
	// 刷新
  mittBus.on('scanDataDoRefresh', () => {
    crudExpose.doRefresh();
  });
	crudExpose.doRefresh();
});

// 页面销毁时，关闭监听布局配置/i18n监听
onUnmounted(() => {
	mittBus.off('scanDataDoRefresh', () => {});
});

</script>
