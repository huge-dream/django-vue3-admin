import { request } from '/@/utils/service';
import { UserPageQuery, AddReq, DelReq, EditReq, InfoReq } from '@fast-crud/fast-crud';
import XEUtils from "xe-utils";

export const apiPrefix = '/api/system/role_api_permission/';
export function GetList(query: UserPageQuery) {
	return request({
		url: apiPrefix,
		method: 'get',
		params: query,
	});
}
export function GetObj(id: InfoReq) {
	return request({
		url: apiPrefix + id,
		method: 'get',
	});
}

export function AddObj(obj: AddReq) {
	return request({
		url: apiPrefix,
		method: 'post',
		data: obj,
	});
}

export function UpdateObj(obj: EditReq) {
	return request({
		url: apiPrefix + obj.id + '/',
		method: 'put',
		data: obj,
	});
}

export function DelObj(id: DelReq) {
	return request({
		url: apiPrefix + id + '/',
		method: 'delete',
		data: { id },
	});
}

/**
 * 获取数据范围授权的所有部门
 * @param query
 * @constructor
 */
export function GetAllDeptData(query: UserPageQuery) {
	return request({
		url: apiPrefix+'role_to_dept_all/',
		method: 'get',
		params: query,
	}).then((res:any)=>{
		return  XEUtils.toArrayTree(res.data,{ parentKey: 'parent', key: 'id', children: 'children',})
	})
}
