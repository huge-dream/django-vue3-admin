import { defineStore } from 'pinia';
import { RoleDrawerType } from '../types';
/**
 * 权限配置：抽屉
 */
const initialState: RoleDrawerType = {
	drawerVisible: false,
	roleId: undefined,
	roleName: undefined,
	users: [],
};

export const RoleDrawerStores = defineStore('RoleDrawerStores', {
	state: (): RoleDrawerType => ({
		...initialState,
	}),
	actions: {
		/**
		 * 打开权限修改抽屉
		 */
		handleDrawerOpen(row: any) {
			this.drawerVisible = true;
			this.set_state(row);
		},
		set_state(row: any) {
			this.roleName = row.name;
			this.roleId = row.id;
			this.users = row.users;
		},
		/**
		 * 关闭权限修改抽屉
		 */
		handleDrawerClose() {
			Object.assign(this.$state, initialState);
		},
	},
});
