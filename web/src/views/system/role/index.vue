<template>
	<fs-page>
		<fs-crud ref="crudRef" v-bind="crudBinding"> </fs-crud>
		<PermissionDrawerCom ref="PermissionDrawerCom" />
	</fs-page>
</template>

<script lang="ts" setup name="role">
import { defineAsyncComponent, onMounted } from 'vue';
import { useFs } from '@fast-crud/fast-crud';
import { createCrudOptions } from './crud';
import { RoleDrawerStores } from './stores/RoleDrawerStores';
import { RoleMenuBtnStores } from './stores/RoleMenuBtnStores';
import { RoleMenuFieldStores } from './stores/RoleMenuFieldStores';

const PermissionDrawerCom = defineAsyncComponent(() => import('./components/RoleDrawer.vue'));

const RoleDrawer = RoleDrawerStores(); // 权限配置抽屉参数
const RoleMenuBtn = RoleMenuBtnStores(); // 角色-菜单
const RoleMenuField = RoleMenuFieldStores();
const { crudBinding, crudRef, crudExpose } = useFs({
	createCrudOptions,
	context: { RoleDrawer, RoleMenuBtn,RoleMenuField },
});

// 页面打开后获取列表数据
onMounted(async () => {
	// 刷新
	crudExpose.doRefresh();
});
</script>
