<template>
	<el-drawer
		v-model="drawerVisibleNew"
		title="权限配置"
		direction="rtl"
		size="60%"
		:close-on-click-modal="false"
		:before-close="handleDrawerClose"
		:destroy-on-close="true"
	>
		<template #header>
			<el-row>
				<el-col :span="4">
					<div>
						当前授权角色：
						<el-tag>{{ props.roleName }}</el-tag>
					</div>
				</el-col>
				<el-col :span="6">
					<div>
						<el-button size="small" type="primary" class="pc-save-btn" @click="handleSavePermission">保存菜单授权 </el-button>
					</div>
				</el-col>
			</el-row>
		</template>
		<div class="permission-com">
			<el-row class="menu-el-row" :gutter="20">
				<el-col :span="6">
					<div class="menu-box menu-left-box">
						<el-tree
							ref="treeRef"
							:data="menuData"
							:props="defaultTreeProps"
							:default-checked-keys="menuDefaultCheckedKeys"
							@check="handleMenuCheck"
							@node-click="handleMenuClick"
							node-key="id"
							check-strictly
							highlight-current
							show-checkbox
							default-expand-all
						>
						</el-tree>
					</div>
				</el-col>

				<el-col :span="18">
					<div class="pc-collapse-main" v-if="menuCurrent.btns && menuCurrent.btns.length > 0">
						<div class="pccm-item">
							<div class="menu-form-alert">配置操作功能接口权限,配置数据权限点击小齿轮</div>
							<el-checkbox v-for="(btn, bIndex) in menuCurrent.btns" :key="bIndex" v-model="btn.isCheck" :label="btn.value">
								<div class="btn-item">
									{{ btn.data_range !== null ? `${btn.name}(${formatDataRange(btn.data_range)})` : btn.name }}
									<span v-show="btn.isCheck" @click.stop.prevent="handleSettingClick(menuCurrent, btn)">
										<el-icon>
											<Setting />
										</el-icon>
									</span>
								</div>
							</el-checkbox>
						</div>

						<div class="pccm-item" v-if="menuCurrent.columns && menuCurrent.columns.length > 0">
							<div class="menu-form-alert">配置数据列字段权限</div>
							<ul class="columns-list">
								<li class="columns-head">
									<div class="width-txt">
										<span>字段</span>
									</div>
									<div v-for="(head, hIndex) in column.header" :key="hIndex" class="width-check">
										<el-checkbox :label="head.value" @change="handleColumnChange($event, menuCurrent, head.value, head.disabled)">
											<span>{{ head.label }}</span>
										</el-checkbox>
									</div>
								</li>

								<li v-for="(c_item, c_index) in menuCurrent.columns" :key="c_index" class="columns-item">
									<div class="width-txt">{{ c_item.title }}</div>
									<div v-for="(col, cIndex) in column.header" :key="cIndex" class="width-check">
										<el-checkbox v-model="c_item[col.value]" class="ci-checkout" :disabled="c_item[col.disabled]"></el-checkbox>
									</div>
								</li>
							</ul>
						</div>
					</div>
				</el-col>
			</el-row>

			<el-dialog v-model="dialogVisible" title="数据权限配置" width="400px" :close-on-click-modal="false" :before-close="handleDialogClose">
				<div class="pc-dialog">
					<el-select v-model="dataPermission" @change="handlePermissionRangeChange" class="dialog-select" placeholder="请选择">
						<el-option v-for="item in dataPermissionRange" :key="item.value" :label="item.label" :value="item.value" />
					</el-select>
					<el-tree-select
						v-show="dataPermission === 4"
						node-key="id"
						v-model="customDataPermission"
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
		</div>
	</el-drawer>
</template>

<script setup lang="ts">
import { ref, onMounted, defineProps, watch, computed, reactive } from 'vue';
import XEUtils from 'xe-utils';
import { errorNotification } from '/@/utils/message';
import { getDataPermissionRange, getDataPermissionDept, getRolePermission, setRolePremission, setBtnDatarange } from './api';
import { MenuDataType, DataPermissionRangeType, CustomDataPermissionDeptType } from './types';
import { ElMessage, ElTree } from 'element-plus';


const props = defineProps({
	roleId: {
		type: Number,
		default: -1,
	},
	roleName: {
		type: String,
		default: '',
	},
	drawerVisible: {
		type: Boolean,
		default: false,
	},
});
const emit = defineEmits(['update:drawerVisible']);

const drawerVisibleNew  = ref(false);
watch(
	() => props.drawerVisible,
	(val) => {
		drawerVisibleNew .value = val;
		getMenuBtnPermission();
		getDataPermissionRangeLable();
		menuCurrent.value = {};
	}
);
const handleDrawerClose = () => {
	emit('update:drawerVisible', false);
};

const defaultTreeProps = {
	children: 'children',
	label: 'name',
	value: 'id',
};

let menuData = ref<MenuDataType[]>([]); // 菜单列表数据
let menuDefaultCheckedKeys = ref<number[]>([]); // 默认选中的菜单列表
let menuCurrent = ref<Partial<MenuDataType>>({}); // 当前选中的菜单

let menuBtnCurrent = ref<number>(-1);
let dialogVisible = ref(false);
let dataPermissionRange = ref<DataPermissionRangeType[]>([]);
let dataPermissionRangeLabel = ref<DataPermissionRangeType[]>([]);

const formatDataRange = computed(() => {
	return function (datarange: number) {
		const findItem = dataPermissionRangeLabel.value.find((i) => i.value === datarange);
		return findItem?.label || '';
	};
});
let deptData = ref<CustomDataPermissionDeptType[]>([]);
let dataPermission = ref();
let customDataPermission = ref([]);

/**
 * 菜单复选框选中
 * @param node
 * @param data
 */
const handleMenuCheck = (node: any, data: any) => {
	XEUtils.eachTree(menuData.value, (item) => {
		item.isCheck = data.checkedKeys.includes(item.id);
	});
};
/**
 * 菜单点击
 * @param node
 * @param data
 */
const handleMenuClick = (selectNode: MenuDataType) => {
	menuCurrent.value = selectNode;
};
//获取菜单,按钮,权限
const getMenuBtnPermission = async () => {
	const resMenu = await getRolePermission({ role: props.roleId });
	menuData.value = resMenu;
	menuDefaultCheckedKeys.value = XEUtils.toTreeArray(resMenu)
		.filter((i) => i.isCheck)
		.map((i) => i.id);
};
// 获取按钮的数据权限下拉选项
const getDataPermissionRangeLable = async () => {
	const resRange = await getDataPermissionRange({ role: props.roleId });
	dataPermissionRangeLabel.value = resRange.data;
};

/**
 * 获取按钮数据权限下拉选项
 * @param btnId  按钮id
 */
const fetchData = async (btnId: number) => {
	try {
		const resRange = await getDataPermissionRange({ menu_button: btnId });
		if (resRange?.code === 2000) {
			dataPermissionRange.value = resRange.data;
		}
	} catch {
		return;
	}
};


/**
 * 设置按钮数据权限
 * @param record 当前菜单
 * @param btnType  按钮类型
 */
const handleSettingClick = (record: any, btn: MenuDataType['btns'][number]) => {
	menuCurrent.value = record;
	menuBtnCurrent.value = btn.id;
	dialogVisible.value = true;
	dataPermission.value = btn.data_range;
	handlePermissionRangeChange(btn.data_range);
	fetchData(btn.id);
};

/**
 * 设置列权限
 * @param val  是否选中
 * @param record  当前菜单
 * @param btnType  按钮类型
 * @param disabledType  禁用类型
 */
const handleColumnChange = (val: boolean, record: any, btnType: string, disabledType: string) => {
	for (const iterator of record.columns) {
		iterator[btnType] = iterator[disabledType] ? iterator[btnType] : val;
	}
};

/**
 * 数据权限设置
 */
const handlePermissionRangeChange = async (val: number) => {
	if (val === 4) {
		const res = await getDataPermissionDept({ role: props.roleId, menu_button: menuBtnCurrent.value });
		const depts = XEUtils.toArrayTree(res.data, { parentKey: 'parent', strict: false });
		deptData.value = depts;
		const btnObj = XEUtils.find(menuCurrent.value.btns, (item) => item.id === menuBtnCurrent.value);
		customDataPermission.value = btnObj.dept;
	}
};

/**
 * 数据权限设置确认
 */
const handleDialogConfirm = () => {
	if (dataPermission.value !== 0 && !dataPermission.value) {
		errorNotification('请选择');
		return;
	}
	for (const btn of menuCurrent.value?.btns || []) {
		if (btn.id === menuBtnCurrent.value) {
			const findItem = dataPermissionRange.value.find((i) => i.value === dataPermission.value);
			btn.data_range = findItem?.value || 0;
			if (btn.data_range === 4) {
				btn.dept = customDataPermission.value;
			}
		}
	}
	handleDialogClose();
};
const handleDialogClose = () => {
	dialogVisible.value = false;
	customDataPermission.value = [];
	dataPermission.value = null;
};

//保存菜单授权
const handleSavePermission = () => {
	setRolePremission(props.roleId, XEUtils.toTreeArray(menuData.value)).then((res: any) => {
		ElMessage({
			message: res.msg,
			type: 'success',
		});
	});
};

const column = reactive({
	header: [
		{ value: 'is_create', label: '新增可见', disabled: 'disabled_create' },
		{ value: 'is_update', label: '编辑可见', disabled: 'disabled_update' },
		{ value: 'is_query', label: '列表可见', disabled: 'disabled_query' },
	],
});

onMounted(() => {});
</script>

<style lang="scss" scoped>
.permission-com {
	margin: 15px;
	box-sizing: border-box;

	.pc-save-btn {
		margin-bottom: 15px;
	}

	.pc-collapse-title {
		line-height: 32px;
		text-align: left;

		span {
			font-size: 16px;
		}
	}

	.pc-collapse-main {
		box-sizing: border-box;

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

	.pc-dialog {
		.dialog-select {
			width: 100%;
		}

		.dialog-tree {
			width: 100%;
			margin-top: 20px;
		}
	}
}
</style>

<style lang="scss">
.permission-com {
	.el-collapse {
		border-top: none;
		border-bottom: none;
	}

	.el-collapse-item {
		margin-bottom: 15px;
	}

	.el-collapse-item__header {
		height: auto;
		padding: 15px;
		border-radius: 8px;
		border-top: 1px solid #ebeef5;
		border-left: 1px solid #ebeef5;
		border-right: 1px solid #ebeef5;
		box-sizing: border-box;
		background-color: #fafafa;
	}

	.el-collapse-item__header.is-active {
		border-radius: 8px 8px 0 0;
		background-color: #fafafa;
	}

	.el-collapse-item__wrap {
		padding: 15px;
		border-left: 1px solid #ebeef5;
		border-right: 1px solid #ebeef5;
		border-top: 1px solid #ebeef5;
		border-radius: 0 0 8px 8px;
		background-color: #fafafa;
		box-sizing: border-box;

		.el-collapse-item__content {
			padding-bottom: 0;
		}
	}
}
</style>
