import { defineStore } from 'pinia';
import { RoleMenuBtnType } from '../types';
/**
 * 权限配置：角色-菜单-按钮
 */

export const RoleMenuBtnStores = defineStore('RoleMenuBtnStores', {
	state: (): RoleMenuBtnType[] => [],
	actions: {
		/**
		 * 初始化
		 */
		setState(data: RoleMenuBtnType[]) {
			this.$state = data;
			this.$state.length = data.length;
		},
		updateState(data: RoleMenuBtnType) {
			const index = this.$state.findIndex((item) => item.id === data.id);
			if (index !== -1) {
				this.$state[index] = data;
			}
		},
	},
});
