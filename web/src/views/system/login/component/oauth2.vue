<template>
	<div class="other-fast-way" v-if="backends.length">
		<div class="fast-title"><span>其他快速方式登录</span></div>
		<ul class="fast-list">
			<li v-for="(v, k) in backends" :key="v">
				<a @click.once="handleOAuth2LoginClick(v)" style="width: 50px;color: #18bc9c">
					<img :src="v.icon" :alt="v.app_name" />
										<p>{{ v.app_name }}</p>

				</a>
			</li>
		</ul>
	</div>
</template>

<script lang="ts">
import { defineComponent, onMounted, reactive, toRefs } from 'vue';
import * as loginApi from '../api';
import { OAuth2Backend } from '/@/views/system/login/types';

export default defineComponent({
	name: 'loginOAuth2',
	setup() {
		const handleOAuth2LoginClick = (backend: OAuth2Backend) => {
			history.replaceState(null, '', location.pathname + location.search);
			window.location.href = backend.authentication_url + '?next=' + window.location.href;
		};
		const state = reactive({
			handleOAuth2LoginClick: handleOAuth2LoginClick,
			backends: [],
		});
		const getBackends = async () => {
			loginApi.getBackends().then((ret: any) => {				
				state.backends = ret.data;
			});
		};
		// const handleTreeClick = (record: MenuTreeItemType) => {
		//   menuButtonRef.value?.handleRefreshTable(record);
		//   menuFieldRef.value?.handleRefreshTable(record)
		// };

		onMounted(() => {
			// getBackends();
		});
		return {
			...toRefs(state),
		};
	},
});
</script>

<style scoped lang="scss">
.login-content-form {
	margin-top: 20px;
	@for $i from 1 through 4 {
		.login-animation#{$i} {
			opacity: 0;
			animation-name: error-num;
			animation-duration: 0.5s;
			animation-fill-mode: forwards;
			animation-delay: calc($i/10) + s;
		}
	}

	.login-content-code {
		width: 100%;
		padding: 0;
	}

	.login-content-submit {
		width: 100%;
		letter-spacing: 2px;
		font-weight: 300;
		margin-top: 15px;
	}

	.login-msg {
		color: var(--el-text-color-placeholder);
	}
}
.other-fast-way {
	//height: 240px;
	position: relative;

	z-index: 1;
	//display: flex;
	//align-items: center;
	//justify-content: center;
	.fast-title {
		display: flex;
		align-items: center;
		justify-content: center;

		span {
			color: #999;
			font-size: 14px;
			padding: 0 20px;
		}
		&:before,
		&:after {
			content: '';
			flex: 1;
			height: 1px;
			background: #ddd;
		}
	}
}
.fast-list {
	display: flex;
	justify-content: center;
	margin-top: 10px;
	li {
		margin-left: 20px;
		opacity: 0;
		animation-name: error-num;
		animation-duration: 0.5s;
		animation-fill-mode: forwards;
		animation-delay: 0.1s;
		a {
			display: block;
			text-align: center;
			cursor: pointer;
			img {
				width: 35px;
				margin: 0 auto;
				max-width: 100%;
				margin-bottom: 6px;
			}
			p {
				font-size: 14px;
				color: #333;
			}
		}
		&:first-child {
			margin-left: 0;
		}
	}
}
</style>
