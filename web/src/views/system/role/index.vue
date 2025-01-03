<template>
	<fs-page>
		<fs-crud ref="crudRef" v-bind="crudBinding"> </fs-crud>
		<PermissionDrawerCom />
	</fs-page>
</template>

<script lang="ts" setup name="role">
import { defineAsyncComponent, onMounted } from 'vue';
import { useFs } from '@fast-crud/fast-crud';
import { createCrudOptions } from './crud';
import { RoleDrawerStores } from './stores/RoleDrawerStores';
import { RoleMenuBtnStores } from './stores/RoleMenuBtnStores';
import { RoleMenuFieldStores } from './stores/RoleMenuFieldStores';
import { RoleUsersStores } from './stores/RoleUsersStores';

const PermissionDrawerCom = defineAsyncComponent(() => import('./components/RoleDrawer.vue'));

const RoleDrawer = RoleDrawerStores(); // 角色-抽屉
const RoleMenuBtn = RoleMenuBtnStores(); // 角色-菜单
const RoleMenuField = RoleMenuFieldStores();// 角色-菜单-字段
const RoleUsers = RoleUsersStores();// 角色-用户
const { crudBinding, crudRef, crudExpose } = useFs({
	createCrudOptions,
	context: { RoleDrawer, RoleMenuBtn, RoleMenuField },
});

// 页面打开后获取列表数据
onMounted(async () => {
	// 刷新
	crudExpose.doRefresh();
	// 获取全部用户
	RoleUsers.get_all_users();

});
</script>
