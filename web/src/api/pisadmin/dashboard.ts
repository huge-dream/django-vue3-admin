import request from '/@/utils/request';

export function getDashboard() {
  return request({
    url: '/api/pisadmin/dashboard/',
    method: 'get',
  });
}
