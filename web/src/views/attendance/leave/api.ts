// // Leave API - Auto-generated on 2024-05-09 16:07:18

import { request } from '/@/utils/service';
import { UserPageQuery, AddReq, DelReq, EditReq, InfoReq } from '@fast-crud/fast-crud';

export const apiPrefix = 'api/leave/';
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

export function approvalObj(obj: EditReq, status: boolean) {
    return request({
        url: apiPrefix + obj.id + '/approve/',
        method: 'put',
        data: {
            status: status ? 1 : 2
        }
    })
}


export function DelObj(id: DelReq) {
	return request({
		url: apiPrefix + id + '/',
		method: 'delete',
		data: { id },
	});
}

export function CalculateLeaveDuration(obj: { start_time: string; end_time: string }) {
	return request({
		url: apiPrefix + 'calculate_leave_duration/',
		method: 'post',
		data: obj,
	});
}
