import { defineStore } from 'pinia';

/**
 * 权限抽屉：角色-用户
 */

export const RoleUserStores = defineStore('RoleUserStores', {
	state: (): any => ({
		drawerVisible: false,
		role_id: undefined,
		role_name: undefined,
	}),
	actions: {
		/**
		 * 打开权限修改抽屉
		 */
		handleDrawerOpen(row: any) {
			this.drawerVisible = true;
			this.role_name = row.name;
			this.role_id = row.id;
		},
		/**
		 * 关闭权限修改抽屉
		 */
		handleDrawerClose() {
			this.drawerVisible = false;
		},
	},
});
