import { request, downloadFile } from '/@/utils/service';
import { PageQuery, AddReq, DelReq, EditReq, InfoReq } from '@fast-crud/fast-crud';

type GetListType = PageQuery & { show_all: string };

export const apiPrefix = '/api/system/user/';

// export function GetDept(query: PageQuery) {
// 	return request({
// 		url: '/api/system/dept/dept_all/',
// 		method: 'get',
// 		params: query,
// 	});
// }

export function GetList(query: GetListType) {
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

export function exportData(params: any) {
	return downloadFile({
		url: apiPrefix + 'export_data/',
		params: params,
		method: 'get',
	});
}

export function getDeptInfoById(id: string, type: string) {
	return request({
		url: `/api/system/dept/dept_info/?dept_id=${id}&show_all=${type}`,
		method: 'get',
	});
}

export function resetPwd(id: number, data: { [key: string]: string }) {
	return request({
		url: `/api/system/user/${id}/reset_password/`,
		method: 'put',
		data,
	});
}
