<template>
	<el-drawer size="70%" v-model="drawer" direction="rtl" destroy-on-close :before-close="handleClose">
    <fs-crud ref="crudRef" v-bind="crudBinding"> </fs-crud>
	</el-drawer>
</template>

<script lang="ts" setup>
import { ref, onMounted, defineAsyncComponent } from 'vue';
import { useFs } from '@fast-crud/fast-crud';
import { createCrudOptions } from './crud';
import { useExpose, useCrud } from '@fast-crud/fast-crud';
import { ElMessageBox } from 'element-plus';

//抽屉是否显示
const drawer = ref(false);

//抽屉关闭确认
const handleClose = (done: () => void) => {
	ElMessageBox.confirm('您确定要关闭?', {
		confirmButtonText: '确定',
		cancelButtonText: '取消',
		type: 'warning',
	})
		.then(() => {
			done();
		})
		.catch(() => {
			// catch error
		});
};

const { crudBinding, crudRef, crudExpose } = useFs({ createCrudOptions, context: {} });
const { setSearchFormData, doRefresh } = crudExpose;

defineExpose({ drawer, setSearchFormData, doRefresh });
// 页面打开后获取列表数据
onMounted(() => {
	crudExpose.doRefresh();
});
</script>
