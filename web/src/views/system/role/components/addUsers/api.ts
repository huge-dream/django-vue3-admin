import { request } from '/@/utils/service';
import { UserPageQuery} from '@fast-crud/fast-crud';

/**
 * 当前角色查询未授权的用户
 * @param role_id 角色id
 * @param query 查询条件 需要有角色id
 * @returns
 */
export function getRoleUsersUnauthorized(query: UserPageQuery) {
	query["authorized"] = 0;  // 未授权的用户
	return request({
		url: '/api/system/role/get_role_users/',
		method: 'get',
		params: query,
	});
}
/**
 * 当前用户角色添加用户
 * @param role_id 角色id
 * @param users_id 用户id数组
 * @returns
 */
export function addRoleUsers(role_id: number, users_id: Array<Number>) {
	return request({ 
		url: `/api/system/role/${role_id}/add_role_users/`,
		method: 'post',
		data: {users_id: users_id},
	});
}