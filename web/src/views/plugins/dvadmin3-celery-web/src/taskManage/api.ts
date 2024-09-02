import { request } from '/@/utils/service';
import { UserPageQuery, AddReq, DelReq, EditReq, InfoReq } from '@fast-crud/fast-crud';

export const apiPrefix = '/api/dvadmin_celery/';
export function getSelectTaskList(query: UserPageQuery) {
	return request({
		url: apiPrefix + 'task/job_list/',
		method: 'get',
		params: query,
	});
}
export function getTaskList(query: UserPageQuery) {
	return request({
		url: apiPrefix + 'periodictask/',
		method: 'get',
		params: query,
	});
}
export function GetTask(id: InfoReq) {
	return request({
		url: apiPrefix + id,
		method: 'get',
	});
}

export function AddTask(obj: AddReq) {
	return request({
		url: apiPrefix,
		method: 'post',
		data: obj,
	});
}

export function UpdateTask(obj: EditReq) {
	return request({
		url: apiPrefix + 'task/' + obj.id + '/update_status/',
		method: 'post',
		data: obj,
	});
}

export function RunTask(obj: AddReq) {
	return request({
		url: apiPrefix + 'task/' + obj.id + '/run_task/',
		method: 'post',
		data: obj,
	});
}

export function DelTask(obj: DelReq) {
	return request({
		url: apiPrefix + 'task/' + obj.id + '/delete_task/',
		method: 'delete',
		data: obj,
	});
}
