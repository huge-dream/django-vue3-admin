import { request } from '/@/utils/service';
import { UserPageQuery} from '@fast-crud/fast-crud';

/**
 * 当前角色查询授权的用户
 * @param query 查询条件 需要有角色id
 * @returns
 */
export function getRoleUsersAuthorized(query: UserPageQuery) {
	query["authorized"] = 1;  // 授权的用户
	return request({
		url: '/api/system/role/get_role_users/',
		method: 'get',
		params: query,
	});
}
/**
 * 当前角色删除授权的用户
 * @param role_id 角色id
 * @param user_id 用户id数组
 * @returns
 */
export function removeRoleUser(role_id: number, user_id: Array<number>) {
	return request({
		url: `/api/system/role/${role_id}/remove_role_user/`,
		method: 'delete',
		data: {user_id: user_id},
	});
}


/**
 * 当前用户角色添加用户
 * @param role_id 角色id
 * @param data 用户id数组
 * @returns
 */
export function addRoleUsers(role_id: number, data: Array<Number>) {
	return request({ 
		url: `/api/system/role/${role_id}/add_role_users/`,
		method: 'post',
		data: {users_id: data},
	});
}