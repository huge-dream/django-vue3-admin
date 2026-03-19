<template>
	<div class="pccm-item" v-if="RoleMenuBtn.$state.length > 0">
		<div class="menu-form-alert">
			<div style="display:flex;  align-items: center; white-space: nowrap; margin-bottom: 10px;">
				<span>默认接口权限:</span>
				<el-select 
					v-model="default_selectBtn.data_range" 
					@change="defaulthandlePermissionRangeChange" 
					placeholder="请选择"
					style="margin-left: 5px; width: 250px; min-width: 250px;"
				>
					<el-option v-for="item in dataPermissionRange" :key="item.value" :label="item.label" :value="item.value" />
				</el-select>
				<el-tree-select
					v-show="default_selectBtn.data_range === 4"
					node-key="id"
					v-model="default_selectBtn.dept"
					:props="defaultTreeProps"
					:data="deptData"
					@change="customhandlePermissionRangeChange(default_selectBtn.dept)" 
					placeholder="请选择自定义部门"
					multiple
					check-strictly
					:render-after-expand="false"
					show-checkbox
					class="dialog-tree"
					style="margin-left: 15px; width: AUTO; min-width: 250px; margin-top: 0;"
				/>

			</div>
			<span>配置操作功能接口权限，配置数据权限点击小齿轮</span>
		</div>

		<el-checkbox v-for="btn in RoleMenuBtn.$state" :key="btn.id" v-model="btn.isCheck" @change="handleCheckChange(btn)">
			<div class="btn-item">
				{{ btn.data_range !== null ? `${btn.name}(${formatDataRange(btn.data_range, btn.dept)})` : btn.name }}
				<span v-show="btn.isCheck" @click.stop.prevent="handleSettingClick(btn)">
					<el-icon>
						<Setting />
					</el-icon>
				</span>
			</div>
		</el-checkbox>
	</div>
	<el-dialog v-model="dialogVisible" title="数据权限配置" width="400px" :close-on-click-modal="false" :before-close="handleDialogClose">
		<div class="pc-dialog">
			<el-select v-model="selectBtn.data_range" @change="handlePermissionRangeChange" placeholder="请选择">
				<el-option v-for="item in dataPermissionRange" :key="item.value" :label="item.label" :value="item.value" />
			</el-select>
			<el-tree-select
				v-show="selectBtn.data_range === 4"
				node-key="id"
				v-model="selectBtn.dept"
				:props="defaultTreeProps"
				:data="deptData"
				multiple
				check-strictly
				:render-after-expand="false"
				show-checkbox
				class="dialog-tree"
			/>
		</div>
		<template #footer>
			<div>
				<el-button type="primary" @click="handleDialogConfirm"> 确定</el-button>
				<el-button @click="handleDialogClose"> 取消</el-button>
			</div>
		</template>
	</el-dialog>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { RoleDrawerStores } from '../stores/RoleDrawerStores';
import { RoleMenuBtnStores } from '../stores/RoleMenuBtnStores';
import { RoleMenuTreeStores } from '../stores/RoleMenuTreeStores';
import { RoleMenuBtnType } from '../types';
import { getRoleToDeptAll, setRoleMenuBtn, setRoleMenuBtnDataRange } from './api';
import XEUtils from 'xe-utils';
import { ElMessage } from 'element-plus';
import { Local } from '/@/utils/storage';

const RoleDrawer = RoleDrawerStores(); // 角色-菜单
const RoleMenuTree = RoleMenuTreeStores(); // 角色-菜单
const RoleMenuBtn = RoleMenuBtnStores(); // 角色-菜单-按钮
const dialogVisible = ref(false);

// 默认按钮
const default_selectBtn = ref<RoleMenuBtnType>({
	id: 0,
	menu_btn_pre_id: 0,
	/** 是否选中 */
	isCheck: false,
	/** 按钮名称 */
	name: '',
	/** 数据权限范围 */
	data_range: Local.get('role_default_data_range'),
	dept: Local.get('role_default_custom_dept'),
});

// 选中的按钮
const selectBtn = ref<RoleMenuBtnType>({
	id: 0,
	menu_btn_pre_id: 0,
	/** 是否选中 */
	isCheck: false,
	/** 按钮名称 */
	name: '',
	/** 数据权限范围 */
	data_range: 0,
	dept: [],
});
/**
 * 数据权限范围
 */
const dataPermissionRange = ref([
	{ label: '仅本人数据权限', value: 0 },
	{ label: '本部门及以下数据权限', value: 1 },
	{ label: '本部门数据权限', value: 2 },
	{ label: '全部数据权限', value: 3 },
	{ label: '自定数据权限', value: 4 },
]);
/**
 * 自定义数据权限的部门树配置
 */
const defaultTreeProps = {
	children: 'children',
	label: 'name',
	value: 'id',
};


/**
 * 默认数据权限下拉选择事件
 * 保留数据到cache
 */
const defaulthandlePermissionRangeChange = async (val: number) => {
	if (val < 4) {
		// default_selectBtn.value.dept = [];
		// Local.set('role_default_custom_dept', []);
	}
	default_selectBtn.value.data_range = val;
	Local.set('role_default_data_range', val);
};

/**
 * 默认部门下拉选择事件
 * 保留数据到cache
 */
 const customhandlePermissionRangeChange = async (dept: Array<number>) => {
	default_selectBtn.value.dept = dept;
	Local.set('role_default_custom_dept', dept);
};

/**
 * 自定数据权限下拉选择事件
 */
const handlePermissionRangeChange = async (val: number) => {
	if (val < 4) {
		selectBtn.value.dept = [];
	}
};
/**
 * 格式化按钮数据范围
 */
const formatDataRange = computed(() => {
	return function (datarange: number, dept: Array<number>) {
		const datarangeitem = XEUtils.find(dataPermissionRange.value, (item: any) => {
			if (item.value === datarange) {
				return item.label;
			}
		});
		// 数据权限与默认数据权限一致
		if (datarange === default_selectBtn.value.data_range) {
			// 判断选择的部门是否一致
			if (datarange !== 4 || JSON.stringify(dept) === JSON.stringify(default_selectBtn.value.dept)) {
				
				return "默认接口权限"
			}
		}
		// datarange === 4 选择的部门不一致返回datarangeitem.label
		return datarangeitem.label;
	};
});
/**
 * 勾选按钮
 */
const handleCheckChange = async (btn: RoleMenuBtnType) => {
	selectBtn.value = default_selectBtn.value;
	const put_data = {
		isCheck: btn.isCheck,
		roleId: RoleDrawer.roleId,
		menuId: RoleMenuTree.id,
		btnId: btn.id,
		data_range: default_selectBtn.value.data_range,
		dept: default_selectBtn.value.dept,
	};
	const { data, msg } = await setRoleMenuBtn(put_data);
	RoleMenuBtn.updateState(data);
	ElMessage({ message: msg, type: 'success' });
};

/**
 * 按钮-数据范围确定
 */
const handleDialogConfirm = async () => {
	const { data, msg } = await setRoleMenuBtnDataRange(selectBtn.value);
	selectBtn.value = data;
	dialogVisible.value = false;
	ElMessage({ message: msg, type: 'success' });
};
/**
 * 数据范围关闭
 */
const handleDialogClose = () => {
	dialogVisible.value = false;
};

/**
 * 齿轮点击
 */
const handleSettingClick = async (btn: RoleMenuBtnType) => {
	selectBtn.value = btn;
	dialogVisible.value = true;
};

/**
 * 部门数据
 *
 */
const deptData = ref<number[]>([]);
// 页面打开后获取列表数据
onMounted(async () => {
	const res = await getRoleToDeptAll({ role: RoleDrawer.roleId, menu_button: selectBtn.value.id });
	const depts = XEUtils.toArrayTree(res.data, { parentKey: 'parent', strict: false });
	deptData.value = depts;
});
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
}

.el-checkbox {
	width: 20%;
}
.btn-item {
	display: flex;
	align-items: center;
	justify-content: center; /* 水平居中 */
	.el-icon {
		margin-left: 5px;
	}
}
.dialog-tree {
	width: 100%;
	margin-top: 20px;
}
</style>
