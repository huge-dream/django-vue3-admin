<template>
	<div class="pccm-item" v-if="RoleMenuField.$state.length > 0">
		<div class="menu-form-alert">
			<el-button size="small" @click="handleSaveField">保存 </el-button>
			配置数据列字段权限
		</div>

		<ul class="columns-list">
			<li class="columns-head">
				<div class="width-txt">
					<span>字段</span>
				</div>
				<div v-for="(head, hIndex) in RoleMenuFieldHeader.$state" :key="hIndex" class="width-check">
					<el-checkbox v-model="head.checked" @change="handleColumnChange($event, head.value, head.disabled)">
						<span>{{ head.label }}</span>
					</el-checkbox>
				</div>
			</li>
			<div class="columns-content">
				<li v-for="(c_item, c_index) in RoleMenuField.$state" :key="c_index" class="columns-item">
					<div class="width-txt">{{ c_item.title }}</div>
					<div v-for="(col, cIndex) in RoleMenuFieldHeader.$state" :key="cIndex" class="width-check">
						<el-checkbox v-model="c_item[col.value]" class="ci-checkout" :disabled="c_item[col.disabled]"></el-checkbox>
					</div>
				</li>
			</div>
		</ul>
	</div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus';
import { RoleDrawerStores } from '../stores/RoleDrawerStores';
import { RoleMenuFieldStores, RoleMenuFieldHeaderStores } from '../stores/RoleMenuFieldStores';
import { setRoleMenuField } from './api';
const RoleMenuField = RoleMenuFieldStores();
const RoleMenuFieldHeader = RoleMenuFieldHeaderStores();
const RoleDrawer = RoleDrawerStores(); // 角色-抽屉
/** 全选 */
const handleColumnChange = (val: boolean, btnType: string, disabledType: string) => {
	for (const iterator of RoleMenuField.$state) {
		iterator[btnType] = iterator[disabledType] ? iterator[btnType] : val;
	}
};
const handleSaveField = async () => {
	const res = await setRoleMenuField(RoleDrawer.$state.roleId, RoleMenuField.$state);
	ElMessage({ message: res.msg, type: 'success' });
};
</script>

<style lang="scss" scoped>
.pccm-item {
	margin-bottom: 10px;
	.menu-form-alert {
		color: #fff;
		line-height: 24px;
		padding: 8px 16px;
		margin-bottom: 20px;
		border-radius: 4px;
		background-color: var(--el-color-primary);
	}
	.menu-form-btn {
		margin-left: 10px;
		height: 40px;
		padding: 8px 16px;
		margin-bottom: 20px;
	}

	.btn-item {
		display: flex;
		align-items: center;

		span {
			margin-left: 5px;
		}
	}

	.columns-list {
		.width-txt {
			width: 200px;
		}

		.width-check {
			width: 100px;
		}

		.width-icon {
			cursor: pointer;
		}

		.columns-head {
			display: flex;
			align-items: center;
			padding: 6px 0;
			border-bottom: 1px solid #ebeef5;
			box-sizing: border-box;

			span {
				font-weight: 900;
			}
		}
		.columns-content {
			max-height: calc(100vh - 240px); /* 视口高度 */
			overflow-y: auto; /* 当内容超出高度时显示垂直滚动条 */
			.columns-item {
				display: flex;
				align-items: center;
				padding: 6px 0;
				box-sizing: border-box;

				.ci-checkout {
					height: auto !important;
				}
			}
		}
	}
}
</style>
