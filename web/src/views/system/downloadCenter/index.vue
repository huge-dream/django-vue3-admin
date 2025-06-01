<template>
	<fs-page>
		<fs-crud ref="crudRef" v-bind="crudBinding">
			<template #cell_url="scope">
				<el-tag size="small">{{ scope.row.url }}</el-tag>
			</template>
		</fs-crud>
	</fs-page>
</template>

<script lang="ts" setup name="downloadCenter">
import { ref, onMounted, inject, onBeforeUpdate } from 'vue';

import { GetPermission } from './api';
import { useExpose, useCrud } from '@fast-crud/fast-crud';
import { createCrudOptions } from './crud';
import PermissionComNew from './components/PermissionComNew/index.vue';
import _ from "lodash-es";
import { handleColumnPermission } from "/@/utils/columnPermission";

// crud组件的ref
const crudRef = ref();
// crud 配置的ref
const crudBinding = ref();

const { crudExpose } = useExpose({ crudRef, crudBinding });

// 你的crud配置
const { crudOptions } = createCrudOptions({ crudExpose });

// 初始化crud配置
const { resetCrudOptions } = useCrud({
	crudExpose,
	crudOptions,
	context: {},
});

// 页面打开后获取列表数据
onMounted(async () => {
	crudExpose.doRefresh();
});
</script>
