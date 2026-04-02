<template>
	<div class="login-container flex z-10">
		<div class="login-left">
			<div class="login-left-logo">
				<img :src="siteLogo" />
				<div class="login-left-logo-text">
					<span>{{ siteBrandTitle }}</span>
				</div>
			</div>
		</div>
		<div class="login-right flex z-10">
			<div class="login-right-warp flex-margin">
				<div class="login-right-warp-mian">
					<div class="login-right-warp-main-title">
						<span>供应商登录</span>
						<br>
						<span>{{userInfos.pwd_change_count===0?'初次登录请修改密码':'欢迎登录'}}</span>
					</div>
					<div class="login-right-warp-main-form">
						<div v-if="!state.isScan">
							<el-tabs v-model="state.tabsActiveName">
								<el-tab-pane :label="$t('message.label.changePwd')" name="changePwd" v-if="userInfos.pwd_change_count===0">
									<ChangePwd />
								</el-tab-pane>
								<el-tab-pane :label="$t('message.label.one1')" name="account" v-else>
									<Account />
								</el-tab-pane>
							</el-tabs>
						</div>
					</div>
				</div>
			</div>
		</div>

		<div class="login-authorization z-10">
			<p>Copyright © AVC 版权所有</p>
		</div>
	</div>
	<div v-if="loginBg">
		<img :src="loginBg" class="loginBg fixed inset-0 z-1 w-full h-full" />
	</div>
</template>

<script setup lang="ts" name="supplierLoginIndex">
import {defineAsyncComponent, onMounted, reactive, computed, watch} from 'vue';
import { storeToRefs } from 'pinia';
import _ from "lodash-es";
import { useThemeConfig } from '/@/stores/themeConfig';
import { SITE_BRAND_TITLE } from '/@/config/brand';
import { NextLoading } from '/@/utils/loading';
import logoMini from '/@/assets/logo-mini.svg';
import loginBg from '/@/assets/supplier-login-bg.jpg';
import { SystemConfigStore } from '/@/stores/systemConfig'
import { useUserInfo } from "/@/stores/userInfo";
const Account = defineAsyncComponent(() => import('/@/views/system/login/component/account.vue'));
const ChangePwd = defineAsyncComponent(() => import('/@/views/system/login/component/changePwd.vue'));

const { userInfos } = storeToRefs(useUserInfo());

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

const siteBrandTitle = 'PIS';
const getThemeConfig = computed(() => themeConfig.value);
const systemConfigStore = SystemConfigStore()
const { systemConfig } = storeToRefs(systemConfigStore)
const getSystemConfig = computed(() => systemConfig.value)

const siteLogo = computed(() => {
	if (!_.isEmpty(getSystemConfig.value['login.site_logo'])) {
		return getSystemConfig.value['login.site_logo']
	}
	return logoMini
});

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
		background-color: rgba(34, 139, 34, 1);
		margin-right: 100px;

		.login-left-logo {
			display: flex;
			align-items: center;
			position: absolute;
			top: 50px;
			left: 80px;
			z-index: 1;

			img {
				width: 80px;
				height: 70px;
			}

			.login-left-logo-text {
				display: flex;
				flex-direction: column;

				span {
					margin-left: 10px;
					font-size: 32px;
					color: #ffffff;
				}
			}
		}
	}

	.login-right {
		width: 700px;

		.login-right-warp {
			border-radius: 3px;
			width: 500px;
			height: 500px;
			position: relative;
			overflow: hidden;

			.login-right-warp-mian {
				display: flex;
				flex-direction: column;
				height: 100%;

				.login-right-warp-main-title {
					height: 130px;
					font-size: 32px;
					font-weight: 600;
					text-align: center;
					letter-spacing: 3px;
					color: var(--el-text-color-primary);
				}

				.login-right-warp-main-form {
					flex: 1;
					padding: 0 50px 50px;
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
			color: #ffffff;
		}
	}
}
</style>
