import { defineStore } from 'pinia';
import { UserInfosStates } from './interface';
import { Session } from '/@/utils/storage';
import { request } from '../utils/service';
/**
 * 用户信息
 * @methods setUserInfos 设置用户信息
 */
export const useUserInfo = defineStore('userInfo', {
	state: (): UserInfosStates => ({
		userInfos: {
			avatar: '',
			username: '',
			name: '',
			email: '',
			mobile: '',
			gender: '',
			dept_info: {
				dept_id: 0,
				dept_name: '',
			},
			role_info: [
				{
					id: 0,
					name: '',
				},
			],
		},
		isSocketOpen: false
	}),
	actions: {
		async updateUserInfos() {
			let userInfos: any = await this.getApiUserInfo();
			this.userInfos.username = userInfos.data.name;
			this.userInfos.avatar = userInfos.data.avatar;
			this.userInfos.name = userInfos.data.name;
			this.userInfos.email = userInfos.data.email;
			this.userInfos.mobile = userInfos.data.mobile;
			this.userInfos.gender = userInfos.data.gender;
			this.userInfos.dept_info = userInfos.data.dept_info;
			this.userInfos.role_info = userInfos.data.role_info;
			Session.set('userInfo', this.userInfos);
		},
		async setUserInfos() {
			// 存储用户信息到浏览器缓存
			if (Session.get('userInfo')) {
				this.userInfos = Session.get('userInfo');
			} else {
				let userInfos: any = await this.getApiUserInfo();
				this.userInfos.username = userInfos.data.name;
				this.userInfos.avatar = userInfos.data.avatar;
				this.userInfos.name = userInfos.data.name;
				this.userInfos.email = userInfos.data.email;
				this.userInfos.mobile = userInfos.data.mobile;
				this.userInfos.gender = userInfos.data.gender;
				this.userInfos.dept_info = userInfos.data.dept_info;
				this.userInfos.role_info = userInfos.data.role_info;
				Session.set('userInfo', this.userInfos);
			}
		},
		async setWebSocketState(socketState: boolean) {
			this.isSocketOpen = socketState;
		},
		async getApiUserInfo() {
			return request({
				url: '/api/system/user/user_info/',
				method: 'get',
			});
		},
	},
});
