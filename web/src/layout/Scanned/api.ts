import { request } from '/@/utils/service';
import { UserPageQuery, AddReq, DelReq, EditReq, InfoReq } from '@fast-crud/fast-crud';

export const apiPrefix = '/api/code_info/scan_data/';

export function AddObj(obj: AddReq) {
	return request({
		url: apiPrefix,
		method: 'post',
		data: obj,
	});
}
