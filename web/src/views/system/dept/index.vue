<template>
	<fs-page>
		<el-row class="dept-el-row">
			<el-col :span="6">
				<div class="dept-box dept-left">
					<DeptTreeCom
						ref="deptTreeRef"
						:treeData="deptTreeData"
						@treeClick="handleTreeClick"
						@updateDept="handleUpdateMenu"
						@deleteDept="handleDeleteMenu"
					/>
				</div>
			</el-col>

			<el-col :span="18">
				<div class="dept-box dept-table">
					<DeptUserCom ref="deptUserRef" />
				</div>
			</el-col>
		</el-row>

		<el-drawer v-model="drawerVisible" title="部门配置" direction="rtl" size="500px" :close-on-click-modal="false" :before-close="handleDrawerClose">
			<DeptFormCom
				v-if="drawerVisible"
				:initFormData="drawerFormData"
				:treeData="deptTreeData"
				:cacheData="deptTreeCacheData"
				@drawerClose="handleDrawerClose"
			/>
		</el-drawer>
	</fs-page>
</template>

<script lang="ts" setup name="dept">
import { ref, onMounted } from 'vue';
import XEUtils from 'xe-utils';
import { ElMessageBox } from 'element-plus';
import DeptTreeCom from './components/DeptTreeCom/index.vue';
import DeptFormCom from './components/DeptFormCom/index.vue';
import DeptUserCom from './components/DeptUserCom/index.vue';
import { GetList, DelObj } from './api';
import { successNotification } from '../../../utils/message';
import { APIResponseData, TreeItemType } from './types';

let deptTreeData = ref([]);
let deptTreeCacheData = ref<TreeItemType[]>([]);
let drawerVisible = ref(false);
let drawerFormData = ref<Partial<TreeItemType>>({});
let deptUserRef = ref<InstanceType<typeof DeptUserCom> | null>(null);
let deptTreeRef = ref<InstanceType<typeof DeptTreeCom> | null>(null);

const getData = async () => {
	let res: APIResponseData = await GetList({});

	if (res?.code === 2000 && Array.isArray(res.data)) {
		const result = XEUtils.toArrayTree(res.data, {
			parentKey: 'parent',
			children: 'children',
			//strict: true,
		});

		deptTreeData.value = result;
	}
};

/**
 * 部门的点击事件
 */
const handleTreeClick = (record: TreeItemType) => {
	deptUserRef.value?.handleDoRefreshUser(record.id as string);
};

/**
 * 部门的删除事件
 */
const handleDeleteMenu = (id: string, callback: Function) => {
	ElMessageBox.confirm('您确认删除该部门吗?', '温馨提示', {
		confirmButtonText: '确认',
		cancelButtonText: '取消',
		type: 'warning',
	}).then(async () => {
		const res: APIResponseData = await DelObj(id);
		callback();
		if (res?.code === 2000) {
			successNotification(res.msg as string);
			getData();
			deptUserRef.value?.handleDoRefreshUser('');
		}
	});
};

/**
 * 部门的 新增 or 编辑 事件
 */
const handleUpdateMenu = (type: string, record?: TreeItemType) => {
	if (type === 'update' && record) {
		const parentData = deptTreeRef.value?.treeRef?.currentNode.parent.data || {};
		deptTreeCacheData.value = [parentData];
		drawerFormData.value = record;
	}
	drawerVisible.value = true;
};
const handleDrawerClose = (type?: string) => {
	if (type === 'submit') {
		getData();
	}
	drawerVisible.value = false;
	drawerFormData.value = {};
};

onMounted(() => {
	getData();
});
</script>

<style lang="scss" scoped>
.dept-el-row {
	height: 100%;
	overflow: hidden;

	.el-col {
		height: 100%;
		padding: 10px 0;
		box-sizing: border-box;
	}
}

.dept-box {
	height: 100%;
	position: relative;
	box-sizing: border-box;
}

.dept-left {
	background-color: var(--el-fill-color-blank);;
	border-radius: 0 8px 8px 0;
	padding: 10px;
}

.dept-table {
	margin-left: 10px;
	padding-bottom: 10px;
}
</style>
