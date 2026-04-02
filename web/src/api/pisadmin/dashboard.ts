import { request } from '/@/utils/service';

const apiPrefix = '/api/pisadmin/dashboard/';

export function getDashboard() {
  return request({
    url: apiPrefix,
    method: 'get',
  });
}
