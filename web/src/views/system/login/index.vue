<template>
	<div class="login-container flex z-10">
		<div class="login-left">
			<div class="login-left-logo">
				<img :src="siteLogo" />
				<div class="login-left-logo-text">
					<span>{{ getSystemConfig['login.site_title'] || getThemeConfig.globalViceTitle }}</span>
					<span class="login-left-logo-text-msg" style="margin-top: 5px;">{{
						getSystemConfig['login.site_name'] || getThemeConfig.globalViceTitleMsg }}</span>
				</div>
			</div>
		</div>
		<div class="login-right flex z-10">
			<div class="login-right-warp flex-margin">
<!--				<span class="login-right-warp-one"></span>-->
<!--				<span class="login-right-warp-two"></span>-->
				<div class="login-right-warp-mian">
					<div class="login-right-warp-main-title">
            {{userInfos.pwd_change_count===0?'初次登录修改密码':'欢迎登录'}}
          </div>
					<div class="login-right-warp-main-form">
						<div v-if="!state.isScan">
							<el-tabs v-model="state.tabsActiveName">
                <el-tab-pane :label="$t('message.label.changePwd')" name="changePwd"  v-if="userInfos.pwd_change_count===0">
                  <ChangePwd />
                </el-tab-pane>
								<el-tab-pane :label="$t('message.label.one1')" name="account" v-else>
									<Account />
								</el-tab-pane>

								<!-- TODO 手机号码登录未接入，展示隐藏 -->
								<!-- <el-tab-pane :label="$t('message.label.two2')" name="mobile">
									<Mobile />
								</el-tab-pane> -->
							</el-tabs>
						</div>
            <OAuth2 />

            <!--						<Scan v-if="state.isScan" />-->
<!--						<div class="login-content-main-sacn" @click="state.isScan = !state.isScan">-->
<!--							<i class="iconfont" :class="state.isScan ? 'icon-diannao1' : 'icon-barcode-qr'"></i>-->
<!--							<div class="login-content-main-sacn-delta"></div>-->
<!--						</div>-->
					</div>
				</div>
			</div>
		</div>

		<div class="login-authorization z-10">
			<p>Copyright © {{ getSystemConfig['login.copyright'] || '2021-2024 北京信码新创科技有限公司' }} 版权所有</p>
			<p class="la-other" style="margin-top: 5px;">
				<a href="https://beian.miit.gov.cn" target="_blank">{{ getSystemConfig['login.keep_record'] ||
					'京ICP备2021031018号' }}</a>
				|
				<a :href="getSystemConfig['login.help_url'] ? getSystemConfig['login.help_url'] : '#'"
					target="_blank">帮助</a>
				|
				<a
					:href="getSystemConfig['login.privacy_url'] ? getBaseURL(getSystemConfig['login.privacy_url']) : '#'">隐私</a>
				|
				<a
					:href="getSystemConfig['login.clause_url'] ? getBaseURL(getSystemConfig['login.clause_url']) : '#'">条款</a>
			</p>
		</div>
	</div>
	<div v-if="loginBg">
		<img :src="loginBg" class="loginBg fixed inset-0 z-1 w-full h-full" />
	</div>
</template>

<script setup lang="ts" name="loginIndex">
import {defineAsyncComponent, onMounted, reactive, computed, watch} from 'vue';
import { storeToRefs } from 'pinia';
import { useThemeConfig } from '/@/stores/themeConfig';
import { NextLoading } from '/@/utils/loading';
import logoMini from '/@/assets/logo-mini.svg';
import loginMain from '/@/assets/login-main.svg';
import loginBg from '/@/assets/login-bg.png';
import { SystemConfigStore } from '/@/stores/systemConfig'
import { getBaseURL } from "/@/utils/baseUrl";
// 引入组件
const Account = defineAsyncComponent(() => import('/@/views/system/login/component/account.vue'));
const Mobile = defineAsyncComponent(() => import('/@/views/system/login/component/mobile.vue'));
const Scan = defineAsyncComponent(() => import('/@/views/system/login/component/scan.vue'));
const ChangePwd = defineAsyncComponent(() => import('/@/views/system/login/component/changePwd.vue'));
const OAuth2 = defineAsyncComponent(() => import('/@/views/system/login/component/oauth2.vue'));

import _ from "lodash-es";
import {useUserInfo} from "/@/stores/userInfo";
const { userInfos } = storeToRefs(useUserInfo());

// 定义变量内容
const storesThemeConfig = useThemeConfig();
const { themeConfig } = storeToRefs(storesThemeConfig);
const state = reactive({
	tabsActiveName: 'account',
	isScan: false,
});


watch(()=>userInfos.value.pwd_change_count,(val)=>{
  if(val===0){
    state.tabsActiveName ='changePwd'
  }else{
    state.tabsActiveName ='account'
  }
},{deep:true,immediate:true})


// 获取布局配置信息
const getThemeConfig = computed(() => {
	return themeConfig.value;
});

const systemConfigStore = SystemConfigStore()
const { systemConfig } = storeToRefs(systemConfigStore)
const getSystemConfig = computed(() => {
	return systemConfig.value
})

const siteLogo = computed(() => {
	if (!_.isEmpty(getSystemConfig.value['login.site_logo'])) {
		return getSystemConfig.value['login.site_logo']
	}
	return logoMini
});

const siteBg = computed(() => {
	if (!_.isEmpty(getSystemConfig.value['login.login_background'])) {
		return getSystemConfig.value['login.login_background']
	}
});

// 页面加载时
onMounted(() => {
	NextLoading.done();
});
</script>

<style scoped lang="scss">
.login-container {
	height: 100%;
	background: var(--el-color-white);

	.login-left {
		flex: 1;
		position: relative;
		background-color: rgba(211, 239, 255, 1);
		margin-right: 100px;

		.login-left-logo {
			display: flex;
			align-items: center;
			position: absolute;
			top: 50px;
			left: 80px;
			z-index: 1;
			animation: logoAnimation 0.3s ease;

			img {
				width: 52px;
				height: 52px;
			}

			.login-left-logo-text {
				display: flex;
				flex-direction: column;

				span {
					margin-left: 10px;
					font-size: 16px;
					color: var(--el-color-primary);
				}

				.login-left-logo-text-msg {
					font-size: 12px;
					color: var(--el-color-primary);
				}
			}
		}

		.login-left-img {
			position: absolute;
			top: 50%;
			left: 50%;
			transform: translate(-50%, -50%);
			width: 100%;
			height: 52%;

			img {
				width: 100%;
				height: 100%;
				animation: error-num 0.6s ease;
			}
		}

		.login-left-waves {
			position: absolute;
			top: 0;
			right: -100px;
		}
	}

	.login-right {
		width: 700px;

		.login-right-warp {
			//border: 1px solid var(--el-color-primary-light-3);
			border-radius: 3px;
			width: 500px;
			height: 500px;
			position: relative;
			overflow: hidden;
			//background-color: var(--el-color-white);

			.login-right-warp-one,
			.login-right-warp-two {
				position: absolute;
				display: block;
				width: inherit;
				height: inherit;

				&::before,
				&::after {
					content: '';
					position: absolute;
					z-index: 1;
				}
			}

			.login-right-warp-one {
				&::before {
					filter: hue-rotate(0deg);
					top: 0px;
					left: 0;
					width: 100%;
					height: 3px;
					background: linear-gradient(90deg, transparent, var(--el-color-primary));
					animation: loginLeft 3s linear infinite;
				}

				&::after {
					filter: hue-rotate(60deg);
					top: -100%;
					right: 2px;
					width: 3px;
					height: 100%;
					background: linear-gradient(180deg, transparent, var(--el-color-primary));
					animation: loginTop 3s linear infinite;
					animation-delay: 0.7s;
				}
			}

			.login-right-warp-two {
				&::before {
					filter: hue-rotate(120deg);
					bottom: 2px;
					right: -100%;
					width: 100%;
					height: 3px;
					background: linear-gradient(270deg, transparent, var(--el-color-primary));
					animation: loginRight 3s linear infinite;
					animation-delay: 1.4s;
				}

				&::after {
					filter: hue-rotate(300deg);
					bottom: -100%;
					left: 0px;
					width: 3px;
					height: 100%;
					background: linear-gradient(360deg, transparent, var(--el-color-primary));
					animation: loginBottom 3s linear infinite;
					animation-delay: 2.1s;
				}
			}

			.login-right-warp-mian {
				display: flex;
				flex-direction: column;
				height: 100%;

				.login-right-warp-main-title {
					height: 130px;
					line-height: 130px;
					font-size: 32px;
          font-weight: 600;
					text-align: center;
					letter-spacing: 3px;
					animation: logoAnimation 0.3s ease;
					animation-delay: 0.3s;
					color: var(--el-text-color-primary);
				}

				.login-right-warp-main-form {
					flex: 1;
					padding: 0 50px 50px;

					.login-content-main-sacn {
						position: absolute;
						top: 2px;
						right: 12px;
						width: 50px;
						height: 50px;
						overflow: hidden;
						cursor: pointer;
						transition: all ease 0.3s;
						color: var(--el-color-primary);

						&-delta {
							position: absolute;
							width: 35px;
							height: 70px;
							z-index: 2;
							top: 2px;
							right: 21px;
							background: var(--el-color-white);
							transform: rotate(-45deg);
						}

						&:hover {
							opacity: 1;
							transition: all ease 0.3s;
							color: var(--el-color-primary) !important;
						}

						i {
							width: 47px;
							height: 50px;
							display: inline-block;
							font-size: 48px;
							position: absolute;
							right: 1px;
							top: 0px;
						}
					}
				}
			}
		}
	}

	.login-authorization {
		position: absolute;
		bottom: 30px;
		left: 0;
		right: 0;
		text-align: center;

		p {
			font-size: 14px;
			color: rgba(0, 0, 0, 0.5);
		}

		a {
			color: var(--el-color-primary);
			margin: 0 5px;
		}
	}
}
</style>
