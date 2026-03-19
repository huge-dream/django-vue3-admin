import { request } from '/@/utils/service';
import { PageQuery, AddReq, DelReq, EditReq, InfoReq } from '@fast-crud/fast-crud';
import { apiPrefix } from '/@/views/system/messageCenter/api';
export function GetUserInfo(query: PageQuery) {
	return request({
		url: '/api/system/user/user_info/',
		method: 'get',
		params: query,
	});
}

/**
 * 更新用户信息
 * @param data
 */
export function updateUserInfo(data: AddReq) {
	return request({
		url: '/api/system/user/update_user_info/',
		method: 'put',
		data: data,
	});
}

/**
 * 获取自己接收的消息
 * @param query
 * @returns {*}
 * @constructor
 */
export function GetSelfReceive(query: PageQuery) {
	return request({
		url: '/api/system/message_center/get_self_receive/',
		method: 'get',
		params: query,
	});
}

/***
 * 修改密码
 * @param data
 */
export function UpdatePassword(data: EditReq) {
	return request({
		url: '/api/system/user/change_password/',
		method: 'put',
		data: data,
	});
}

/***
 * 上传头像
 * @param data
 */
export function uploadAvatar(data: AddReq) {
	return request({
		url: 'api/system/file/',
		method: 'post',
		data: data,
		headers: {
			'Content-Type': 'multipart/form-data',
		},
	});
}
