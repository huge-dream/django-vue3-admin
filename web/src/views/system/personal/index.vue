<template>
	<div class="home-container">
    <div style="margin: 15px; font-size: 16px; font-weight: 700">
    <span :style="{ color: headerTextColor }">{{ currentTime }}，{{ state.personalForm.username }}</span>
      <span style="font-size: 12px; color: grey">{{$t('message.personal.PersonalInfo1')}}</span>
    </div>
		<el-row>

			<!-- 个人信息 -->
			<el-col :span="16"  class="home-card-two mb15">
        <el-row>
          <div class="home-card-item" style="height: 380px">
            <el-row>
            <el-col  :span="12">
              <div class="home-card-item-title">{{$t('message.personal.MyInfo')}}</div>
						<div>
							<avatarSelector v-model="selectImgVisible" @uploadImg="uploadImg" ref="avatarSelectorRef"></avatarSelector>
						</div>
						<div>
							<el-row>
								<el-col :span="24">
									<el-row>
										<el-col class="personal-item mb6">
                      <div style="display: flex;">
                        <div style="flex: 1;">昵称：</div>
                        <div style="flex: 1;">{{ state.personalForm.name }}</div>
                      </div>
										</el-col>
										<el-col class="personal-item mb6">
                      <div style="display: flex;">
                        <div style="flex: 1;">部门：</div>
                        <div style="flex: 1;"><el-tag>{{ state.personalForm.dept_info.dept_name }}</el-tag></div>
                      </div>
										</el-col>
                    <el-col class="personal-item mb6">
                      <div style="display: flex;">
                        <div style="flex: 1;">角色：</div>
                        <div style="flex: 1;"><el-tag v-for="(item, index) in state.personalForm.role_info" :key="index" style="margin-right: 5px">{{ item.name }}</el-tag></div>
                      </div>
										</el-col>
									</el-row>
								</el-col>
							</el-row>
						</div>
            <div class="home-card-item-title">{{$t('message.personal.AccountSecurity')}}</div>
            <el-col class="personal-item mb6">
                      <div style="display: flex;">
                        <div style="flex: 1;">当前密码强度：强</div>
                        <div style="flex: 1;"><el-button text type="primary" @click="passwordFormShow = true">立即修改
                                        <el-icon class="el-icon--right"><Edit /></el-icon>
                        </el-button></div>

                      </div>
            </el-col>
            <el-col class="personal-item mb6">
                      <div style="display: flex;">
                        <div style="flex: 1;">已绑定手机：</div>
                        <div style="flex: 1;">{{ state.personalForm.mobile }}</div>
                      </div>
            </el-col>
            <el-col class="personal-item mb6">
                      <div style="display: flex;">
                        <div style="flex: 1;">已绑定邮箱：</div>
                        <div style="flex: 1;">{{ state.personalForm.email }}</div>
                      </div>
            </el-col>
          </el-col>
          <el-col  :span="12">
            <div class="home-card-item-title">{{$t('message.personal.UpdateInfo')}}</div>
            <el-form :model="state.personalForm" :rules="rules" ref="userInfoFormRef" label-width="80px">
          <el-row :gutter="35">
							<el-col >
								<el-form-item label="昵称" prop="name">
									<el-input v-model="state.personalForm.name" placeholder="请输入昵称" clearable></el-input>
								</el-form-item>
							</el-col>
							<el-col>
								<el-form-item label="邮箱">
									<el-input v-model="state.personalForm.email" placeholder="请输入邮箱" clearable></el-input>
								</el-form-item>
							</el-col>
							<el-col>
								<el-form-item label="手机" prop="mobile">
									<el-input v-model="state.personalForm.mobile" placeholder="请输入手机" clearable></el-input>
								</el-form-item>
							</el-col>
							<el-col>
								<el-form-item label="性别">
									<el-select v-model="state.personalForm.gender" placeholder="请选择性别" clearable class="w100">
										<!--										<el-option label="男" :value="1"></el-option>-->
										<!--										<el-option label="女" :value="0"></el-option>-->
										<!--										<el-option label="保密" :value="2"></el-option>-->
										<el-option v-for="(item, index) in genderList" :key="index" :label="item.label" :value="item.value"></el-option>
									</el-select>
								</el-form-item>
							</el-col>
							<el-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24">
								<el-form-item>
									<el-button type="primary" @click="submitForm">
										{{$t('message.personal.UpdateInfo')}}
                    <el-icon>
											<ele-Position />
										</el-icon>
									</el-button>
								</el-form-item>
							</el-col>
						</el-row>
            </el-form>
          </el-col>
          </el-row>
        </div>
        </el-row>
        <el-row>
          <div style="margin-top: 15px">
            <div class="home-card-item" :style="{ height: '185px', background: smokeTextBgColor, display: 'flex', alignItems: 'center', padding: '20px'}">
            <div class="smoke-text-container">
              <p class="smoke-text" ref="smokeTextRef" :style="{ color: smokeTextColor }">
                {{$t('message.personal.PersonalInfo2')}}
              </p>
            </div>
          </div>
          </div>
        </el-row>
			</el-col>

			<!-- 消息通知 -->
      <el-col :span="8"   class="home-card-one mb15" >
        <div style="margin-left: 30px">
          <div class="home-card-item" style=" width:350px; height: 100%; max-height: 580px;" >
              <div class="home-card-item-title">{{$t('message.router.systemNotice')}}
                <button   type="button" class="el-button" style=" float: right; border-color: transparent; margin-top: -2px;" @click="msgMore">
                  <span>{{$t('message.home.more')}}
              <i class="el-icon fs-icon fs-button-icon-right"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024"><path fill="currentColor" d="M512 160c320 0 512 352 512 352S832 864 512 864 0 512 0 512s192-352 512-352m0 64c-225.28 0-384.128 208.064-436.8 288 52.608 79.872 211.456 288 436.8 288 225.28 0 384.128-208.064 436.8-288-52.608-79.872-211.456-288-436.8-288m0 64a224 224 0 1 1 0 448 224 224 0 0 1 0-448m0 64a160.19 160.19 0 0 0-160 160c0 88.192 71.744 160 160 160s160-71.808 160-160-71.744-160-160-160"></path></svg></i>
              </span>
                </button>
              </div>
						<div v-for="(item, index) in state.newsInfoList" :key="index" class="personal-info-li flex-margin flex w100" >
              <div class="home-card-item-icon flex" style="margin: 5px;" :style="{ background: `#f8f8f8` }">
                <i class="flex-margin font24" :class="`fa fa-commenting-o`" :style="{ color: `#5d8b22` }"></i>
						</div>
              <div class="flex-auto" style="margin-top: 10px">
							  <span class="font14">[{{ item.creator_name }}]</span>
							  <span style=" color: grey; float: right; font-style:italic;">&nbsp;{{ item.create_datetime }}&nbsp;&nbsp;</span>
							  <div class="text-container" style="font-size: 12px; margin-top: 5px"> {{ item.title }}</div>
						  </div>
						</div>
            </div>
        </div>
		</el-col>
    </el-row>
    <el-row>

		</el-row>
		<!--    密码修改-->
		<el-dialog v-model="passwordFormShow" title="密码修改">
			<el-form
				ref="userPasswordFormRef"
				:model="userPasswordInfo"
				required-asterisk
				label-width="100px"
				label-position="left"
				:rules="passwordRules"
				center
			>
				<el-form-item label="原密码" required prop="oldPassword">
					<el-input type="password" v-model="userPasswordInfo.oldPassword" placeholder="请输入原始密码" show-password clearable></el-input>
				</el-form-item>
				<el-form-item required prop="newPassword" label="新密码">
					<el-input type="password" v-model="userPasswordInfo.newPassword" placeholder="请输入新密码" show-password clearable></el-input>
				</el-form-item>
				<el-form-item required prop="newPassword2" label="确认密码">
					<el-input type="password" v-model="userPasswordInfo.newPassword2" placeholder="请再次输入新密码" show-password clearable></el-input>
				</el-form-item>
			</el-form>
			<template #footer>
				<span class="dialog-footer">
					<el-button type="primary" @click="settingPassword"> <i class="fa fa-check"></i>提交 </el-button>
				</span>
			</template>
		</el-dialog>
	</div>
</template>

<script setup lang="ts" name="personal">
import { reactive, computed, onMounted, ref, defineAsyncComponent, nextTick, watch } from 'vue';
import { formatAxis } from '/@/utils/formatTime';
import * as api from './api';
import { ElMessage } from 'element-plus';
import { getBaseURL } from '/@/utils/baseUrl';
import { Session } from '/@/utils/storage';
import { useRouter } from 'vue-router';
import { useUserInfo } from '/@/stores/userInfo';
import { useThemeConfig } from '/@/stores/themeConfig';
import { successMessage } from '/@/utils/message';
import { dictionary } from '/@/utils/dictionary';
import { Md5 } from 'ts-md5';
import { Edit } from '@element-plus/icons-vue';

interface NewsItem {
	creator_name: string;
	create_datetime: string;
	title: string;
}

interface PersonalState {
	newsInfoList: NewsItem[];
	personalForm: {
		avatar: string;
		username: string;
		name: string;
		email: string;
		mobile: string;
		gender: string | number;
		dept_info: {
			dept_id: number;
			dept_name: string;
		};
		role_info: Array<{
			id: number;
			name: string;
		}>;
	};
}

const router = useRouter();
const themeConfigStore = useThemeConfig();

const avatarSelector = defineAsyncComponent(() => import('/@/components/avatarSelector/index.vue'));
const avatarSelectorRef = ref<any>(null);
const smokeTextRef = ref<HTMLElement | null>(null);
const currentTime = computed(() => {
	return formatAxis(new Date());
});

const isDark = computed(() => {
	return themeConfigStore.themeConfig.isIsDark;
});

const smokeTextBgColor = computed(() => {
	return isDark.value ? '#191919' : '#fff';
});

const smokeTextColor = computed(() => {
	return isDark.value ? '#fff' : '#000';
});

const headerTextColor = computed(() => {
	return isDark.value ? '#e6e6e6' : '#000000';
});
const userInfoFormRef = ref();
const rules = reactive({
	name: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
	mobile: [{ pattern: /^1[3-9]\d{9}$/, message: '请输入正确手机号' }],
});

let selectImgVisible = ref(false);

const state = reactive<PersonalState>({
	newsInfoList: [],
	personalForm: {
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
});


/**
 * 跳转消息中心
 */
const route = useRouter();
const msgMore = () => {
	route.push({ path: '/messageCenter' });
};

const genderList = ref();
/**
 * 获取用户个人信息
 */
const getUserInfo = function () {
	api.GetUserInfo({}).then((res: any) => {
		const { data } = res;
		genderList.value = dictionary('gender');
		state.personalForm.avatar = data.avatar || '';
		state.personalForm.username = data.username || '';
		state.personalForm.name = data.name || '';
		state.personalForm.email = data.email || '';
		state.personalForm.mobile = data.mobile || '';
		state.personalForm.gender = data.gender;
		state.personalForm.dept_info.dept_name = data.dept_info.dept_name || '';
		state.personalForm.role_info = data.role_info || [];
	});
};

/**
 * 更新用户信息
 * @param formEl
 */
const submitForm = async () => {
	if (!userInfoFormRef.value) return;
	await userInfoFormRef.value.validate((valid: boolean, fields: any) => {
		if (valid) {
			api.updateUserInfo(state.personalForm).then((res: any) => {
				ElMessage.success('更新成功');
				getUserInfo();
			});
		} else {
			ElMessage.error('表单验证失败,请检查~');
		}
	});
};

/**
 * 获取消息通知
 */
const getMsg = async () => {
	try {
		const res = await api.GetSelfReceive({});
		const { data } = res || {};
		
		if (data && Array.isArray(data) && data.length > 0) {
			state.newsInfoList = data.map((item: any) => ({
				creator_name: String(item.creator_name || '未知用户'),
				create_datetime: String(item.create_datetime || ''),
				title: String(item.title || ''),
			}));
		} else {
			state.newsInfoList = [];
		}
	} catch (error) {
		console.error('Failed to fetch messages:', error);
		state.newsInfoList = [];
	}
};
onMounted(() => {
	getUserInfo();
	getMsg();
	nextTick(() => {
		initSmokeText();
	});
});

watch(() => themeConfigStore.themeConfig.globalI18n, () => {
	nextTick(() => {
		initSmokeText();
	});
});

const initSmokeText = () => {
	if (smokeTextRef.value) {
		const text = smokeTextRef.value;
		text.innerHTML = text.textContent.replace(/\S/g, "<span>$&</span>");
		const spans = text.querySelectorAll('span');
		for (let i = 0; i < spans.length; i++) {
			spans[i].addEventListener("mouseover", () => {
				spans[i].classList.add('action');
			});
		}
	}
};

/**************************密码修改部分************************/
const passwordFormShow = ref(false);
const userPasswordFormRef = ref();
const userPasswordInfo = reactive({
	oldPassword: '',
	newPassword: '',
	newPassword2: '',
});

const validatePass = (rule: any, value: any, callback: any) => {
	const pwdRegex = new RegExp('(?=.*[0-9])(?=.*[a-zA-Z]).{8,30}');
	if (value === '') {
		callback(new Error('请输入密码'));
	} else if (value === userPasswordInfo.oldPassword) {
		callback(new Error('原密码与新密码一致'));
	} else if (!pwdRegex.test(value)) {
		callback(new Error('您的密码复杂度太低(密码中必须包含字母、数字)'));
	} else {
		if (userPasswordInfo.newPassword2 !== '') {
			userPasswordFormRef.value.validateField('newPassword2');
		}
		callback();
	}
};
const validatePass2 = (rule: any, value: any, callback: any) => {
	if (value === '') {
		callback(new Error('请再次输入密码'));
	} else if (value !== userPasswordInfo.newPassword) {
		callback(new Error('两次输入密码不一致!'));
	} else {
		callback();
	}
};

const passwordRules = reactive({
	oldPassword: [
		{
			required: true,
			message: '请输入原密码',
			trigger: 'blur',
		},
	],
	newPassword: [{ validator: validatePass, trigger: 'blur' }],
	newPassword2: [{ validator: validatePass2, trigger: 'blur' }],
});

/**
 * 重新设置密码
 */
const settingPassword = () => {
	userPasswordFormRef.value.validate((valid: boolean) => {
		if (valid) {
			api.UpdatePassword(userPasswordInfo).then((res: any) => {
				ElMessage.success('密码修改成功');
				setTimeout(() => {
					Session.remove('token');
					router.push('/login');
				}, 1000);
			});
		} else {
			// 校验失败
			// 登录表单校验失败
			ElMessage.error('表单校验失败，请检查');
		}
	});
};

const uploadImg = (data: any) => {
	let formdata = new FormData();
	formdata.append('file', data);
	api.uploadAvatar(formdata).then((res: any) => {
		if (res.code === 2000) {
			selectImgVisible.value = false;
			// state.personalForm.avatar = getBaseURL() + res.data.url;
			state.personalForm.avatar = res.data.url;
			api.updateUserInfo(state.personalForm).then((_res: any) => {
				successMessage('更新成功');
				getUserInfo();
				useUserInfo().updateUserInfos();
				if (avatarSelectorRef.value && typeof avatarSelectorRef.value.updateAvatar === 'function') {
					avatarSelectorRef.value.updateAvatar(state.personalForm.avatar);
				}
			});
		}
	});
};
</script>

<style scoped lang="scss">
$homeNavLengh: 8;

.smoke-text-container {
	width: 100%;
	height: 100%;
	display: flex;
	align-items: center;
	justify-content: center;
}

.smoke-text {
	font-size: 16px;
	line-height: 24px;
	text-align: left;
	width: 100%;
}

.smoke-text :deep(span) {
	position: relative;
	display: inline-block;
	cursor: pointer;
}

.smoke-text :deep(span.action) {
	animation: smoke 2s linear forwards;
	transform-origin: bottom;
}

@keyframes smoke {
	0% {
		opacity: 1;
		filter: blur(0);
		transform: translateX(0) translateY(0) rotate(0deg) scale(1);
	}
	50% {
		opacity: 1;
		pointer-events: none;
	}
	100% {
		opacity: 0;
		filter: blur(20px);
		transform: translateX(300px) translateY(-300px) rotate(720deg) scale(4);
	}
}

.text-container {
width: 420px;
white-space: nowrap;
overflow: hidden;
text-overflow: ellipsis;
}
.text-container:hover {
animation: scrollText 5s linear infinite;
}
@keyframes scrollText {
0% { transform: translateX(0); }
100% { transform: translateX(-100%); }
}

.home-container {
  overflow: hidden;

  // 基础卡片样式
  .home-card-item {
    width: 100%;
    transition: all ease 0.3s;
    padding: 20px;
    overflow: hidden;
    background: var(--el-color-white);
    color: var(--el-text-color-primary);
    border: 1px solid var(--next-border-color-light);
    border-radius: 24px;

    &:hover {
      box-shadow: 0 2px 12px var(--next-color-dark-hover);
    }

    &-icon {
      width: 55px;
      height: 55px;
      border-radius: 100%;
      flex-shrink: 1;

      i {
        color: var(--el-text-color-placeholder);
      }
    }

    &-title {
      font-size: 16px;
      font-weight: bold;
      height: 30px;
    }
  }

  // 卡片组一（小卡片）
  .home-card-one {
    left:15px;
    right: 15px;

    .home-card-item {
      height: 120px;  // 小卡片高度
    }

    @for $i from 0 through 3 {
      .home-one-animation#{$i} {
        opacity: 0;
        animation-name: error-num;
        animation-duration: 0.5s;
        animation-fill-mode: forwards;
        animation-delay: calc($i/10) + s;
      }
    }
  }

  // 卡片组二和三（大卡片）
  .home-card-two, .home-card-three {
    position: relative;
    left: 15px;
    right: 15px;

    .home-card-item {
      height: 400px;  // 大卡片高度
      width: 100%;
      overflow: hidden;

      .home-monitor {
        height: 100%;

        .flex-warp-item {
          width: 25%;
          height: 111px;
          display: flex;

          .flex-warp-item-box {
            margin: auto;
            text-align: center;
            color: var(--el-text-color-primary);
            display: flex;
            border-radius: 5px;
            background: var(--next-bg-color);
            cursor: pointer;
            transition: all 0.3s ease;

            &:hover {
              background: var(--el-color-primary-light-9);
            }
          }

          @for $i from 0 through 3 {
            .home-animation#{$i} {
              opacity: 0;
              animation-name: error-num;
              animation-duration: 0.5s;
              animation-fill-mode: forwards;
              animation-delay: calc($i/10) + s;
            }
          }
        }
      }
    }
  }
}
</style>
