<template>
	<fs-page>
		<fs-crud ref="crudRef" v-bind="crudBinding">
			<template #header-middle>
				<el-tabs v-model="tabActivted" @tab-click="onTabClick">
					<el-tab-pane label="我的发布" name="send"></el-tab-pane>
					<el-tab-pane label="我的接收" name="receive"></el-tab-pane>
				</el-tabs>
			</template>
		</fs-crud>
	</fs-page>
</template>

<script lang="ts" setup name="messageCenter">
import { ref, onMounted } from 'vue';
import { useFs } from '@fast-crud/fast-crud';
import createCrudOptions from './crud';

//tab选择
const tabActivted = ref('send');
const onTabClick = (tab: any) => {
	const { paneName } = tab;
	tabActivted.value = paneName;
	crudExpose.doRefresh();
};

const context: any = { tabActivted }; //将 tabActivted 通过context传递给crud.tsx
// 初始化crud配置
const { crudRef, crudBinding, crudExpose } = useFs({ createCrudOptions, context });

// 页面打开后获取列表数据
onMounted(() => {
	crudExpose.doRefresh();
});
</script>
