import { defineStore } from 'pinia';
import { UserInfosStates } from './interface';
import { Session } from '/@/utils/storage';
import { request } from '../utils/service';
import { getBaseURL } from '../utils/baseUrl';
import headerImage from '/@/assets/img/headerImage.png';

/**
 * 用户信息
 * @methods setUserInfos 设置用户信息
 */
export const useUserInfo = defineStore('userInfo', {
	state: (): UserInfosStates => ({
		userInfos: {
			id:'',
			avatar: '',
			username: '',
			name: '',
			email: '',
			mobile: '',
			gender: '',
			pwd_change_count:null,
			is_superuser: false,
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
		async setPwdChangeCount(count: number) {
			this.userInfos.pwd_change_count = count;
		},
		async updateUserInfos(userInfos:any) {
			this.userInfos.id = userInfos.id;
			this.userInfos.username = userInfos.name;
			this.userInfos.avatar = userInfos.avatar;
			this.userInfos.name = userInfos.name;
			this.userInfos.email = userInfos.email;
			this.userInfos.mobile = userInfos.mobile;
			this.userInfos.gender = userInfos.gender;
			this.userInfos.dept_info = userInfos.dept_info;
			this.userInfos.role_info = userInfos.role_info;
			this.userInfos.pwd_change_count = userInfos.pwd_change_count;
			this.userInfos.is_superuser = userInfos.is_superuser;
			Session.set('userInfo', this.userInfos);
		},
		async setUserInfos() {
			// 存储用户信息到浏览器缓存
			if (Session.get('userInfo')) {
				this.userInfos = Session.get('userInfo');
			} else {
				let userInfos: any = await this.getApiUserInfo();
				this.userInfos.id = userInfos.id;
				this.userInfos.username = userInfos.data.name;
				this.userInfos.avatar = userInfos.data.avatar;
				this.userInfos.name = userInfos.data.name;
				this.userInfos.email = userInfos.data.email;
				this.userInfos.mobile = userInfos.data.mobile;
				this.userInfos.gender = userInfos.data.gender;
				this.userInfos.dept_info = userInfos.data.dept_info;
				this.userInfos.role_info = userInfos.data.role_info;
				this.userInfos.pwd_change_count = userInfos.data.pwd_change_count;
				this.userInfos.is_superuser = userInfos.data.is_superuser;
				Session.set('userInfo', this.userInfos);
			}
		},
		async getApiUserInfo() {
			return request({
				url: '/api/system/user/user_info/',
				method: 'get',
			}).then((res:any)=>{
				this.userInfos.id = res.data.id;
				this.userInfos.username = res.data.name;
				this.userInfos.avatar = (res.data.avatar && getBaseURL(res.data.avatar)) || headerImage;
				this.userInfos.name = res.data.name;
				this.userInfos.email = res.data.email;
				this.userInfos.mobile = res.data.mobile;
				this.userInfos.gender = res.data.gender;
				this.userInfos.dept_info = res.data.dept_info;
				this.userInfos.role_info = res.data.role_info;
				this.userInfos.pwd_change_count = res.data.pwd_change_count;
				this.userInfos.is_superuser = res.data.is_superuser;
				Session.set('userInfo', this.userInfos);
			})
		},
	},
});
