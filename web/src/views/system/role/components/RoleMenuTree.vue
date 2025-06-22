<template>
	<el-tree
		ref="treeRef"
		:data="menuData"
		:props="defaultTreeProps"
		:default-checked-keys="menuDefaultCheckedKeys"
		@check-change="handleMenuChange"
		@node-click="handleMenuClick"
		node-key="id"
		check-strictly
		highlight-current
		show-checkbox
		default-expand-all
		:check-on-click-leaf="false"
	>
	</el-tree>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { RoleDrawerStores } from '../stores/RoleDrawerStores';
import { RoleMenuTreeStores } from '../stores/RoleMenuTreeStores';
import { RoleMenuBtnStores } from '../stores/RoleMenuBtnStores';
import { RoleMenuFieldStores } from '../stores/RoleMenuFieldStores';
import { RoleMenuFieldHeaderStores } from '../stores/RoleMenuFieldStores';
import { getRoleMenu, getRoleMenuBtnField, setRoleMenu } from './api';
import { ElMessage } from 'element-plus';
import XEUtils from 'xe-utils';
import { RoleMenuTreeType } from '../types';

const RoleDrawer = RoleDrawerStores(); // 角色-抽屉
const RoleMenuTree = RoleMenuTreeStores(); // 角色-菜单
const RoleMenuBtn = RoleMenuBtnStores(); // 角色-菜单-按钮
const RoleMenuField = RoleMenuFieldStores(); // 角色-菜单-列字段
const RoleMenuFieldHeader = RoleMenuFieldHeaderStores();// 角色-菜单-列字段
const menuData = ref<RoleMenuTreeType[]>([]); // 菜单列表数据
const menuDefaultCheckedKeys = ref<(number | string | undefined)[]>([]); // 默认选中的菜单列表
// 菜单配置
const defaultTreeProps = {
	children: 'children',
	label: 'name',
	value: 'id',
};

/**
 * 菜单复选框选中
 * @param node：当前节点的 Node 对象
 * @param checked：布尔值，表示当前节点是否被选中
 */
const handleMenuChange = (node: any, checked: boolean) => {
	setRoleMenu({ roleId: RoleDrawer.roleId, menuId: node.id, isCheck: checked }).then((res: any) => {
		ElMessage({ message: res.msg, type: 'success' });
	});
};
/**
 * 菜单点击事件
 */
const handleMenuClick = async (selectNode: RoleMenuTreeType) => {
	if (!selectNode.is_catalog) {
		RoleMenuTree.setRoleMenuTree(selectNode); // 更新当前选中的菜单
		// 获取当前菜单的按钮列表
		const { data } = await getRoleMenuBtnField({
			roleId: RoleDrawer.roleId,
			menuId: selectNode.id,
		});
		RoleMenuBtn.setState(data.menu_btn); // 更新按钮列表
		RoleMenuField.setState(data.menu_field); // 更新列字段列表
	} else {
		RoleMenuBtn.setState([]); // 更新按钮列表
		RoleMenuField.setState([]); // 更新列字段列表
	}
	RoleMenuFieldHeader.$reset()
};

// 页面打开后获取列表数据
onMounted(async () => {
	menuData.value = await getRoleMenu({ roleId: RoleDrawer.roleId });
	menuDefaultCheckedKeys.value = XEUtils.toTreeArray(menuData.value)
		.filter((i) => i.isCheck)
		.map((i) => i.id);
});
</script>
