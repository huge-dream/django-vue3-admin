import { defineStore } from 'pinia';
import { RoleMenuTreeType } from '../types';
/**
 * 权限抽屉：角色-菜单
 */

export const RoleMenuTreeStores = defineStore('RoleMenuTreeStores', {
	state: (): RoleMenuTreeType => ({
		id: 0,
		parent: 0,
		name: '',
		isCheck: false,
		is_catalog: false,
	}),
	actions: {
		/** 赋值 */
		setRoleMenuTree(data: RoleMenuTreeType) {
			this.$state = data;
		},
	},
});
