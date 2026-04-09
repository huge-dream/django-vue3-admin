<template>
	<div class="menu-btn-com" :style="{ height: 'calc(72vh - 44px)' }">
		<!-- 批量操作工具栏 -->
		<div v-if="selectedRowsCount > 0" class="batch-toolbar">
			<span class="batch-tip">
				<el-icon><Check /></el-icon>
				{{ t('message.pages.menu.buttons.selectedTip', { count: selectedRowsCount }) }}
			</span>
			<el-button size="small" @click="clearSelection">{{ t('message.pages.menu.buttons.clearSelection') }}</el-button>
			<el-button size="small" type="danger" plain :icon="Delete" @click="handleBatchDelete">
				{{ t('message.pages.menu.buttons.batchDelete') }}
			</el-button>
		</div>

		<fs-crud ref="crudRef" v-bind="crudBinding" style="height: 100%">
			<template #pagination-right>
				<el-text type="info" size="small">{{ t('message.pages.menu.buttons.totalCount', { count: totalCount }) }}</el-text>
			</template>
		</fs-crud>
	</div>
</template>

<script lang="ts" setup>
import { computed, ref } from 'vue';
import { useFs } from '@fast-crud/fast-crud';
import { createCrudOptions } from './crud';
import { MenuTreeItemType } from '../../types';
import { ElMessage, ElMessageBox } from 'element-plus';
import XEUtils from 'xe-utils';
import { BatchDelete } from './api';
import { Close, Delete, Check } from '@element-plus/icons-vue';
import { useThemeConfig } from '/@/stores/themeConfig';
import { storeToRefs } from 'pinia';

const { themeConfig } = storeToRefs(useThemeConfig());

const { t } = useI18n();

let selectOptions: any = ref({ name: null });

const { crudRef, crudBinding, crudExpose, context,selectedRows } = useFs({ createCrudOptions, context: { selectOptions } });
const { doRefresh, setTableData } = crudExpose;

// 选中行的条数
const selectedRowsCount = computed(() => {
	return selectedRows.value.length;
});

// 总条数
const totalCount = computed(() => {
	return crudBinding.value?.pagination?.total || 0;
});

// 批量删除
const handleBatchDelete = async () => {
	await ElMessageBox.confirm(`确定要批量删除这${selectedRows.value.length}条记录吗`, '确认', {
		distinguishCancelAndClose: true,
		confirmButtonText: '确定',
		cancelButtonText: '取消',
		closeOnClickModal: false,
		type: 'warning',
	});
	await BatchDelete(XEUtils.pluck(selectedRows.value, 'id'));
	ElMessage.success(t('message.pages.menu.messages.deleteSuccess'));
	selectedRows.value = [];
	await crudExpose.doRefresh();
};

// 清除选择
const clearSelection = () => {
	const tableRef = crudExpose.getBaseTableRef();
	const tableData = crudExpose.getTableData();
	XEUtils.arrayEach(tableData, (row: any) => {
		tableRef.toggleRowSelection(row, false);
	});
	selectedRows.value = [];
};

const handleRefreshTable = (record: MenuTreeItemType) => {
	if (!record.is_catalog && record.id) {
		selectOptions.value = record;
		doRefresh();
	} else {
		setTableData([]);
	}
};

defineExpose({ selectOptions, handleRefreshTable });
</script>

<style lang="scss" scoped>
.menu-btn-com {
	height: 100%;
	overflow: hidden;
	display: flex;
	flex-direction: column;

	.batch-toolbar {
		display: flex;
		align-items: center;
		gap: 12px;
		padding: 8px 12px;
		margin-bottom: 8px;
		background-color: var(--el-fill-color-light);
		border-radius: 4px;
		border: 1px solid var(--el-border-color-lighter);

		.batch-tip {
			display: flex;
			align-items: center;
			gap: 4px;
			color: var(--el-color-primary);
			font-size: 13px;

			strong {
				font-weight: 600;
			}
		}
	}
}
</style>
