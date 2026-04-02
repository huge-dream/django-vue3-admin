import request from '/@/utils/request';

export function getDashboard() {
  return request({
    url: '/pisadmin/dashboard/',
    method: 'get',
  });
}
