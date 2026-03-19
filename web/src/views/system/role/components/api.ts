import { request } from '/@/utils/service';
import XEUtils from 'xe-utils';
/**
 * 获取 角色-菜单
 * @param query
 */
export function getRoleMenu(query: object) {
	return request({
		url: '/api/system/role_menu_button_permission/get_role_menu/',
		method: 'get',
		params: query,
	}).then((res: any) => {
		return XEUtils.toArrayTree(res.data, { key: 'id', parentKey: 'parent', children: 'children', strict: false });
	});
}
/**
 * 设置 角色-菜单
 * @param data
 * @returns
 */
export function setRoleMenu(data: object) {
	return request({
		url: '/api/system/role_menu_button_permission/set_role_menu/',
		method: 'put',
		data,
	});
}
/**
 * 获取 角色-菜单-按钮-列字段
 * @param query
 */
export function getRoleMenuBtnField(query: object) {
	return request({
		url: '/api/system/role_menu_button_permission/get_role_menu_btn_field/',
		method: 'get',
		params: query,
	});
}

/**
 * 设置 角色-菜单-按钮
 * @param data
 */
export function setRoleMenuBtn(data: object) {
	return request({
		url: '/api/system/role_menu_button_permission/set_role_menu_btn/',
		method: 'put',
		data,
	});
}

/**
 * 设置 角色-菜单-列字段
 * @param data
 */
export function setRoleMenuField(roleId: string | number | undefined, data: object) {
	return request({
		url: `/api/system/role_menu_button_permission/${roleId}/set_role_menu_field/`,
		method: 'put',
		data,
	});
}

/**
 * 设置 角色-菜单-按钮-数据权限
 * @param query
 * @returns
 */
export function setRoleMenuBtnDataRange(data: object) {
	return request({
		url: '/api/system/role_menu_button_permission/set_role_menu_btn_data_range/',
		method: 'put',
		data,
	});
}

/**
 * 获取当前用户角色下所能授权的部门
 * @param query
 * @returns
 */
export function getRoleToDeptAll(query: object) {
	return request({
		url: '/api/system/role_menu_button_permission/role_to_dept_all/',
		method: 'get',
		params: query,
	});
}

/**
 * 获取所有用户
 * @param query
 * @returns
 */
export function getAllUsers() {
	return request({
		url: '/api/system/user/',
		method: 'get',
		params: { limit: 999 },
	}).then((res: any) => {
		return XEUtils.map(res.data, (item: any) => {
			return {
				id: item.id,
				name: item.name,
			};
		});
	});
}

/**
 * 设置角色-用户
 * @param query
 * @returns
 */
export function setRoleUsers(roleId: string | number | undefined, data: object) {
	return request({
		url: `/api/system/role/${roleId}/set_role_users/`,
		method: 'put',
		data,
	});
}
