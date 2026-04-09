<template>
	<fs-page>
		<el-row class="menu-el-row">
			<el-col :span="6">
				<div class="menu-box menu-left-box">
					<MenuTreeCom
						ref="menuTreeRef"
						:treeData="menuTreeData"
						@treeClick="handleTreeClick"
						@updateDept="handleUpdateMenu"
						@deleteDept="handleDeleteMenu"
					/>
				</div>
			</el-col>

			<el-col :span="18">
        <el-tabs type="border-card">
          <el-tab-pane :label="$t('message.pages.menu.dialog.buttonPermission')" >
            <div class="menu-btn-pane">
              <div class="menu-scan-btn">
                <el-button type="primary" @click="handleOpenScanModal">
                  <el-icon><Monitor /></el-icon>
                  {{ $t('message.pages.menu.scan.title') }}
                </el-button>
              </div>
              <MenuButtonCom ref="menuButtonRef" class="menu-btn-fill" />
            </div>
          </el-tab-pane>
          <el-tab-pane label="列权限配置">
            <div style="height: 72vh">
              <MenuFieldCom ref="menuFieldRef"></MenuFieldCom>
            </div>
          </el-tab-pane>
        </el-tabs>

				<ScanModal
					ref="scanModalRef"
					v-model="scanModalVisible"
					:menuId="selectedMenuId"
					@success="handleScanSuccess"
				/>

			</el-col>
		</el-row>

		<el-drawer v-model="drawerVisible" title="菜单配置" direction="rtl" size="500px" :close-on-click-modal="false" :before-close="handleDrawerClose">
			<MenuFormCom
				v-if="drawerVisible"
				:initFormData="drawerFormData"
				:cacheData="menuTreeCacheData"
				:treeData="menuTreeData"
				@drawerClose="handleDrawerClose"
			/>
		</el-drawer>
	</fs-page>
</template>

<script lang="ts" setup name="menuPages">
import { ref, onMounted, nextTick } from 'vue';
import XEUtils from 'xe-utils';
import { ElMessageBox, ElMessage } from 'element-plus';
import MenuTreeCom from './components/MenuTreeCom/index.vue';
import MenuButtonCom from './components/MenuButtonCom/index.vue';
import MenuFormCom from './components/MenuFormCom/index.vue';
import MenuFieldCom from './components/MenuFieldCom/index.vue';
import ScanModal from './components/ScanModal/index.vue';
import { GetList, DelObj } from './api';
import { successNotification } from '/@/utils/message';
import { APIResponseData, MenuTreeItemType } from './types';

let menuTreeData = ref([]);
let menuTreeCacheData = ref<MenuTreeItemType[]>([]);
let drawerVisible = ref(false);
let drawerFormData = ref<Partial<MenuTreeItemType>>({});
let menuTreeRef = ref<InstanceType<typeof MenuTreeCom> | null>(null);
let menuButtonRef = ref<InstanceType<typeof MenuButtonCom> | null>(null);
let menuFieldRef = ref<InstanceType<typeof MenuFieldCom> | null>(null);
let selectedMenuId = ref<number | null>(null);
let scanModalVisible = ref(false);
let scanModalRef = ref<any>(null);
const getData = () => {
	GetList({}).then((ret: APIResponseData) => {
		const responseData = ret.data;
		const result = XEUtils.toArrayTree(responseData, {
			parentKey: 'parent',
			children: 'children',
			strict: true,
		});
		menuTreeData.value = result;
	});
};

/**
 * 菜单的点击事件
 */
const handleTreeClick = (record: MenuTreeItemType) => {
	selectedMenuId.value = record.id ?? null;
	menuButtonRef.value?.handleRefreshTable(record);
  menuFieldRef.value?.handleRefreshTable(record)
};

/**
 * 部门的 新增 or 编辑 事件
 */
const handleUpdateMenu = (type: string, record?: MenuTreeItemType) => {
	if (type === 'update' && record) {
		const parentData = menuTreeRef.value?.treeRef?.currentNode.parent.data || {};
		menuTreeCacheData.value = [parentData];
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

const handleOpenScanModal = () => {
	if (!selectedMenuId.value) {
		ElMessage.warning('请先选择一个菜单');
		return;
	}
	scanModalVisible.value = true;
	nextTick(() => {
		scanModalRef.value?.handleOpen();
	});
};

const handleScanSuccess = () => {
	if (selectedMenuId.value) {
		menuButtonRef.value?.handleRefreshTable({ id: selectedMenuId.value });
	}
};

/**
 * 部门的删除事件
 */
const handleDeleteMenu = (id: string, callback: Function) => {
	ElMessageBox.confirm('您确认删除该菜单项吗?', '温馨提示', {
		confirmButtonText: '确认',
		cancelButtonText: '取消',
		type: 'warning',
	}).then(async () => {
		const res: APIResponseData = await DelObj(id);
		callback();
		if (res?.code === 2000) {
			successNotification(res.msg as string);
			getData();
		}
	});
};

onMounted(() => {
	getData();
});
</script>

<style lang="scss" scoped>
.menu-el-row {
	height: 100%;
	overflow: hidden;

	.el-col {
		height: 100%;
		padding: 10px 0;
		box-sizing: border-box;
	}
}

.menu-box {
	height: 100%;
	padding: 10px;
	background-color: var(--el-fill-color-blank);;
	box-sizing: border-box;
}

.menu-left-box {
	position: relative;
	border-radius: 0 8px 8px 0;
	margin-right: 10px;
}

.menu-right-box {
	border-radius: 8px 0 0 8px;
}

.menu-scan-btn {
	display: flex;
	justify-content: flex-end;
	margin-bottom: 8px;
}

.menu-btn-pane {
	display: flex;
	flex-direction: column;
	height: 100%;

	.menu-btn-fill {
		flex: 1;
		overflow: hidden;
	}
}
</style>
