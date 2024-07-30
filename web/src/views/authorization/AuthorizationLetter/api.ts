// // AuthorizationLetter API - Auto-generated on 2024-07-15 16:30:40

import { request } from '/@/utils/service';
import { UserPageQuery, AddReq, DelReq, EditReq, InfoReq } from '@fast-crud/fast-crud';



export const apiPrefix = 'api/authorization/letter/';

export function GenerateAuthorizationLetter(id: InfoReq) {
	return request({
		url: apiPrefix + id + '/generate/',
		method: 'get',
	});
}

export function DownloadAuthorizationLetter(id: InfoReq) {
	return request({
		url: apiPrefix + id + '/download/',
		method: 'get',
		responseType: 'blob',
	});
}

export async function ClearAuthorizationLetter() {
	return request({
		url: apiPrefix + 'clear/',
		method: 'get',
	});
}
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