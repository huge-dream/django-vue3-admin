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
			<div class="alert-toolbar">
				<span>{{ $t('message.pages.role.dialog.configureOperationPermission') }}</span>
				<el-button size="small" link type="primary" @click="expandAll">{{ $t('message.pages.role.buttons.expandAll') }}</el-button>
				<el-button size="small" link type="primary" @click="collapseAll">{{ $t('message.pages.role.buttons.collapseAll') }}</el-button>
			</div>
		</div>

		<!-- 按 Model > CRUD 语义分组的折叠面板 -->
		<el-collapse v-model="expandedModels" class="btn-group-collapse">
			<el-collapse-item
				v-for="modelGroup in groupedButtons"
				:key="modelGroup.model"
				:name="modelGroup.model"
			>
				<template #title>
					<div class="model-group-header">
						<el-checkbox
							:model-value="isModelAllSelected(modelGroup)"
							:indeterminate="isModelIndeterminate(modelGroup)"
							@change="(val: boolean) => toggleModel(modelGroup, val)"
							@click.stop
						/>
						<el-icon style="margin: 0 6px;"><Folder /></el-icon>
						<span class="model-label">{{ modelGroup.model }}</span>
						<span class="group-count">{{ getTotalCount(modelGroup) }} {{ $t('message.pages.menu.scan.actions') }}</span>
					</div>
				</template>

				<!-- CRUD 语义子分组 -->
				<div class="intent-groups">
					<div
						v-for="intent in modelGroup.intents"
						:key="intent.type"
						class="intent-group"
					>
						<div class="intent-header">
							<el-checkbox
								:model-value="isIntentAllSelected(intent)"
								:indeterminate="isIntentIndeterminate(intent)"
								@change="(val: boolean) => toggleIntent(modelGroup, intent, val)"
								@click.stop
							/>
							<el-tag :type="intentTagType(intent.type)" size="small" style="margin-left: 6px;">{{ intent.label }}</el-tag>
						</div>
						<div class="btn-checkboxes">
							<el-checkbox
								v-for="btn in intent.buttons"
								:key="btn.id"
								v-model="btn.isCheck"
								@change="handleCheckChange(btn)"
								class="btn-checkbox-item"
							>
								<div class="btn-item">
									<span>{{ btn.name }}</span>
									<span v-show="btn.isCheck" @click.stop.prevent="handleSettingClick(btn)">
										<el-icon><Setting /></el-icon>
									</span>
								</div>
							</el-checkbox>
						</div>
					</div>
				</div>
			</el-collapse-item>
		</el-collapse>
	</div>

	<el-dialog v-model="dialogVisible" :title="$t('message.pages.role.dialog.dataPermissionConfig')" width="400px" :close-on-click-modal="false" :before-close="handleDialogClose">
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
import { getRoleToDeptAll, batchSetRoleMenuBtn, setRoleMenuBtnDataRange } from './api';
import { Folder, Setting } from '@element-plus/icons-vue';
import XEUtils from 'xe-utils';
import { ElMessage } from 'element-plus';
import { Local } from '/@/utils/storage';

/** CRUD 语义类型 */
type IntentType = 'read' | 'write' | 'delete' | 'other';

/** 按 intent 分组的按钮列表 */
interface IntentGroup {
	type: IntentType;
	label: string;
	buttons: RoleMenuBtnType[];
}

/** 按 model 分组的按钮列表 */
interface ModelGroup {
	model: string;
	intents: IntentGroup[];
}

const RoleDrawer = RoleDrawerStores();
const RoleMenuTree = RoleMenuTreeStores();
const RoleMenuBtn = RoleMenuBtnStores();
const dialogVisible = ref(false);

const default_selectBtn = ref<RoleMenuBtnType>({
	id: 0,
	menu_btn_pre_id: 0,
	isCheck: false,
	name: '',
	data_range: Local.get('role_default_data_range'),
	dept: Local.get('role_default_custom_dept'),
});

const selectBtn = ref<RoleMenuBtnType>({
	id: 0,
	menu_btn_pre_id: 0,
	isCheck: false,
	name: '',
	data_range: 0,
	dept: [],
});

const t = (key: string) => i18n.global.t(key);

const dataPermissionRange = ref([
	{ label: '仅本人数据权限', value: 0 },
	{ label: '本部门及以下数据权限', value: 1 },
	{ label: '本部门数据权限', value: 2 },
	{ label: '全部数据权限', value: 3 },
	{ label: '自定数据权限', value: 4 },
]);

const defaultTreeProps = {
	children: 'children',
	label: 'name',
	value: 'id',
};

/** CRUD 意图映射配置 */
const INTENT_CONFIG: Record<IntentType, { keywords: string[]; labelKey: string; order: number }> = {
	read: {
		keywords: ['list', 'retrieve', 'export', 'search', 'query', 'detail', 'info', 'get'],
		labelKey: 'message.pages.role.buttons.intentRead',
		order: 1,
	},
	write: {
		keywords: ['create', 'update', 'patch', 'import', 'copy', 'add', 'edit', 'save', 'submit'],
		labelKey: 'message.pages.role.buttons.intentWrite',
		order: 2,
	},
	delete: {
		keywords: ['delete', 'remove', 'destroy'],
		labelKey: 'message.pages.role.buttons.intentDelete',
		order: 3,
	},
	other: {
		keywords: [],
		labelKey: 'message.pages.role.buttons.intentOther',
		order: 4,
	},
};

/** 根据 action 名称判断 CRUD 意图 */
const getIntentType = (action: string): IntentType => {
	const lower = action.toLowerCase();
	for (const [type, config] of Object.entries(INTENT_CONFIG)) {
		if (config.keywords.some(kw => lower.includes(kw))) {
			return type as IntentType;
		}
	}
	return 'other';
};

/** CRUD 意图标签颜色 */
const intentTagType = (type: IntentType): string => {
	const map: Record<IntentType, string> = {
		read: 'success',
		write: 'primary',
		delete: 'danger',
		other: 'info',
	};
	return map[type];
};

const expandedModels = ref<string[]>([]);

/** 按 Model > CRUD 意图分组 */
const groupedButtons = computed(() => {
	// value 格式: app:model:action
	// 示例: system:User:List, test_app:Blog:Create
	const modelMap: Map<string, Map<IntentType, RoleMenuBtnType[]>> = new Map();

	for (const btn of RoleMenuBtn.$state) {
		const value = (btn as any).value || '';
		const parts = value.split(':');
		const model = parts[1] || parts[0] || 'other';
		const action = parts[2] || '';

		if (!modelMap.has(model)) {
			modelMap.set(model, new Map());
		}
		const intentMap = modelMap.get(model)!;

		const intentType = getIntentType(action);
		if (!intentMap.has(intentType)) {
			intentMap.set(intentType, []);
		}
		intentMap.get(intentType)!.push(btn);
	}

	const groups = [] as Array<{ model: string; intents: IntentGroup[] }>;
	for (const [model, intentMap] of modelMap) {
		// 按固定顺序排列 CRUD 意图
		const intentTypes = (Object.keys(INTENT_CONFIG) as IntentType[])
			.filter(type => intentMap.has(type))
			.sort((a, b) => INTENT_CONFIG[a].order - INTENT_CONFIG[b].order);
		const intents = intentTypes.map(type => ({
			type,
			label: i18n.global.t(INTENT_CONFIG[type].labelKey),
			buttons: intentMap.get(type)!,
		}));
		groups.push({ model, intents });
	}

	// 按 model 名称排序
	groups.sort((a, b) => a.model.localeCompare(b.model));
	return groups;
});

/** 展开/折叠全部 */
const expandAll = () => {
	expandedModels.value = groupedButtons.value.map(g => g.model);
};
const collapseAll = () => {
	expandedModels.value = [];
};

/** Model 全选/半选 */
const isModelAllSelected = (modelGroup: ModelGroup) => {
	const allBtns = modelGroup.intents.flatMap(i => i.buttons);
	return allBtns.length > 0 && allBtns.every(btn => btn.isCheck);
};

const isModelIndeterminate = (modelGroup: ModelGroup) => {
	const allBtns = modelGroup.intents.flatMap(i => i.buttons);
	const selected = allBtns.filter(btn => btn.isCheck).length;
	return selected > 0 && selected < allBtns.length;
};

const toggleModel = (modelGroup: ModelGroup, checked: boolean) => {
	for (const intent of modelGroup.intents) {
		for (const btn of intent.buttons) {
			btn.isCheck = checked;
			markChange(btn);
		}
	}
};

/** CRUD 意图全选/半选 */
const isIntentAllSelected = (intent: IntentGroup) => {
	return intent.buttons.length > 0 && intent.buttons.every(btn => btn.isCheck);
};

const isIntentIndeterminate = (intent: IntentGroup) => {
	const selected = intent.buttons.filter(btn => btn.isCheck).length;
	return selected > 0 && selected < intent.buttons.length;
};

const toggleIntent = (_modelGroup: ModelGroup, intent: IntentGroup, checked: boolean) => {
	for (const btn of intent.buttons) {
		btn.isCheck = checked;
		markChange(btn);
	}
};

/** 获取 Model 分组的总按钮数 */
const getTotalCount = (modelGroup: ModelGroup) => {
	return modelGroup.intents.reduce((sum, i) => sum + i.buttons.length, 0);
};

/** 防抖 + 批量更新 */
const pendingChanges = new Map<string | number, { btn: RoleMenuBtnType; isCheck: boolean }>();
const flushTimer = ref<ReturnType<typeof setTimeout> | null>(null);
const isFlushing = ref(false);

const markChange = (btn: RoleMenuBtnType) => {
	pendingChanges.set(btn.id, { btn, isCheck: btn.isCheck });
	scheduleFlush();
};

const scheduleFlush = () => {
	if (flushTimer.value !== null) {
		clearTimeout(flushTimer.value);
	}
	flushTimer.value = setTimeout(() => {
		flushChanges();
	}, 300);
};

const flushChanges = async () => {
	if (isFlushing.value || pendingChanges.size === 0) return;
	isFlushing.value = true;
	const changes = Array.from(pendingChanges.values());
	pendingChanges.clear();
	flushTimer.value = null;

	const buttons = changes.map(c => ({
		btnId: c.btn.id,
		isCheck: c.isCheck,
		data_range: default_selectBtn.value.data_range,
		dept: default_selectBtn.value.dept,
	}));

	try {
		const res: any = await batchSetRoleMenuBtn({
			roleId: RoleDrawer.roleId,
			menuId: RoleMenuTree.id,
			buttons,
		});
		ElMessage({ message: res.msg || `已更新 ${buttons.length} 项`, type: 'success' });
	} catch (err: any) {
		ElMessage({ message: err?.message || '更新失败', type: 'error' });
	} finally {
		isFlushing.value = false;
	}
};

/** 单个 checkbox 变更 */
const handleCheckChange = (btn: RoleMenuBtnType) => {
	markChange(btn);
};

const handleDialogConfirm = async () => {
	const { data, msg } = await setRoleMenuBtnDataRange(selectBtn.value);
	selectBtn.value = data;
	dialogVisible.value = false;
	ElMessage({ message: msg, type: 'success' });
};

const handleDialogClose = () => {
	dialogVisible.value = false;
};

const handleSettingClick = async (btn: RoleMenuBtnType) => {
	selectBtn.value = btn;
	dialogVisible.value = true;
};

const defaulthandlePermissionRangeChange = async (val: number) => {
	default_selectBtn.value.data_range = val;
	Local.set('role_default_data_range', val);
};

const customhandlePermissionRangeChange = async (dept: Array<number>) => {
	default_selectBtn.value.dept = dept;
	Local.set('role_default_custom_dept', dept);
};

const handlePermissionRangeChange = async (val: number) => {
	if (val < 4) {
		selectBtn.value.dept = [];
	}
};

const deptData = ref<number[]>([]);

onMounted(async () => {
	const res = await getRoleToDeptAll({ role: RoleDrawer.roleId, menu_button: selectBtn.value.id });
	const depts = XEUtils.toArrayTree(res.data, { parentKey: 'parent', strict: false });
	deptData.value = depts;
	expandedModels.value = groupedButtons.value.map(g => g.model);
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
	.alert-toolbar {
		display: flex;
		align-items: center;
		justify-content: space-between;
		span {
			color: #fff;
		}
	}
}

.btn-group-collapse {
	border: 1px solid var(--el-border-color);
	border-radius: 4px;
	overflow: hidden;
}

.model-group-header {
	display: flex;
	align-items: center;
	font-size: 14px;
	font-weight: 500;
	width: 100%;
	padding-right: 12px;

	.model-label {
		margin-left: 4px;
		font-weight: 600;
	}

	.group-count {
		margin-left: auto;
		font-size: 12px;
		color: #909399;
		font-weight: normal;
	}
}

.intent-groups {
	padding: 8px 0 8px 8px;
}

.intent-group {
	margin-bottom: 12px;
	&:last-child {
		margin-bottom: 0;
	}

	.intent-header {
		display: flex;
		align-items: center;
		margin-bottom: 6px;
		padding-bottom: 4px;
		border-bottom: 1px solid var(--el-border-color-lighter);
	}
}

.btn-checkboxes {
	display: flex;
	flex-wrap: wrap;
	gap: 4px 16px;
	padding-left: 20px;
}

.btn-checkbox-item {
	min-width: 120px;
}

.btn-item {
	display: flex;
	align-items: center;
	gap: 4px;
	.el-icon {
		color: var(--el-color-primary);
	}
}

.dialog-tree {
	width: 100%;
	margin-top: 20px;
}
</style>
