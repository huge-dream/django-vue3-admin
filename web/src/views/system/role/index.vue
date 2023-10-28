<template>
	<fs-page>
		<fs-crud ref="crudRef" v-bind="crudBinding">
			<template #cell_url="scope">
				<el-tag size="small">{{ scope.row.url }}</el-tag>
			</template>
		</fs-crud>

		<PermissionComNew v-model:drawerVisible="drawerVisible" :roleId="roleId" :roleName="roleName" @drawerClose="handleDrawerClose" />
	</fs-page>
</template>

<script lang="ts" setup name="role">
import { ref, onMounted, inject } from 'vue';
import { useColumnPermission } from '/@/stores/columnPermission';
import { GetPermission } from './api';
import { useExpose, useCrud } from '@fast-crud/fast-crud';
import { createCrudOptions } from './crud';
import permission from './components/PermissionCom/index.vue';
import PermissionComNew from './components/index.vue';

let drawerVisible = ref(false);
let roleId = ref(null);
let roleName = ref(null);

const rolePermission = ref();
// crud组件的ref
const crudRef = ref();
// crud 配置的ref
const crudBinding = ref();

const hasPermissions: any = inject('$hasPermissions');

const fetchColumnPermission = async () => {
	const res = await GetPermission();
	useColumnPermission().setPermissionData(res.data);
};

const handleDrawerOpen = (row: any) => {
	roleId.value = row.id;
	roleName.value = row.name;
	drawerVisible.value = true;
};

const handleDrawerClose = () => {
	drawerVisible.value = false;
};

const { crudExpose } = useExpose({ crudRef, crudBinding });

// 页面打开后获取列表数据
onMounted(async () => {
	await fetchColumnPermission();

	// 你的crud配置
	const { crudOptions } = createCrudOptions({ crudExpose, rolePermission, handleDrawerOpen, hasPermissions });

	// 初始化crud配置
	const { resetCrudOptions } = useCrud({
		crudExpose,
		crudOptions,
		context: {},
	});

	crudExpose.doRefresh();
});

</script>
