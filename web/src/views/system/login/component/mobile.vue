<template>
	<el-form  size="large" class="login-content-form">
		<el-form-item class="login-animation1" >
			<el-input  type="text" :placeholder="$t('message.mobile.placeholder1')" v-model="ruleForm.username" clearable autocomplete="off">
				<template #prefix>
					<i class="iconfont icon-dianhua el-input__icon"></i>
				</template>
			</el-input>
		</el-form-item>
		<el-form-item class="login-animation2">
			<el-col :span="16">
				<el-input type="text" maxlength="4"  :placeholder="$t('message.mobile.placeholder2')" v-model="ruleForm.code" clearable autocomplete="off">
					<template #prefix>
						<el-icon class="el-input__icon"><ele-Position /></el-icon>
					</template>
				</el-input>
			</el-col>
			<el-col :span="1"></el-col>
			<el-col :span="7">
				<el-button class="login-content-code" style="border-radius: 8px !important;">{{ $t('message.mobile.codeText') }}</el-button>
			</el-col>
		</el-form-item>
		<el-form-item class="login-animation3">
			<el-button round type="primary" class="login-content-submit">
				<span>{{ $t('message.mobile.btnText') }}</span>
			</el-button>
		</el-form-item>
		<div class="font12 mt30 login-animation4 login-msg" style="color:grey">{{ $t('message.mobile.msgText') }}</div>
	</el-form>
</template>

<script lang="ts">
import { toRefs, reactive, defineComponent } from 'vue';

// 定义接口来定义对象的类型
interface LoginMobileState {
	username: any;
	code: string | number | undefined;
}

// 定义对象与类型
const ruleForm: LoginMobileState = {
	username: '',
	code: '',
};

export default defineComponent({
	name: 'loginMobile',
	setup() {
		const state = reactive({ ruleForm });
		return {
			...toRefs(state),
		};
	},
});
</script>

<style scoped lang="scss">
.login-content-form {
	margin-top: 20px;

	// 为输入框添加圆角和设置字体大小
	:deep(.el-input__wrapper) {
		border-radius: 8px !important;
	}
	// 设置输入框文字大小
	:deep(.el-input__inner) {
		font-size: 12px !important; // Element Plus large尺寸的默认字体大小
	}

	@for $i from 1 through 4 {
		.login-animation#{$i} {
			opacity: 0;
			animation-name: error-num;
			animation-duration: 0.5s;
			animation-fill-mode: forwards;
			animation-delay: #{ $i/10 }s;
		}
	}

	.login-content-password {
		display: inline-block;
		width: 20px;
		cursor: pointer;

		&:hover {
			color: #909397;
		}
	}

	.login-content-captcha {
		width: 100%;
		padding: 0;
		font-weight: bold;
		letter-spacing: 5px;
    border-radius: 8px !important;
	}

	.login-content-submit {
		width: 100%;
		letter-spacing: 2px;
		font-weight: 800;
		margin-top: 15px;
    border-radius:8px;
	}
}
</style>
