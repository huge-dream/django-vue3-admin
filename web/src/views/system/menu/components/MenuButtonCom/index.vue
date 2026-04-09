<template>
	<div class="menu-btn-com" :style="{ height: 'calc(72vh - 44px)' }">
		<!-- 批量操作工具栏 -->
		<div v-if="selectedRowsCount > 0 || isSelectable" class="batch-toolbar">
			<span class="batch-tip">
				<el-icon><Check /></el-icon>
				{{ t('message.pages.menu.buttons.selectedTip', { count: selectedRowsCount }) }}
			</span>
			<el-button size="small" :disabled="totalCount === 0" @click="handleSelectAll">{{ t('message.pages.menu.buttons.selectAll') }}</el-button>
			<el-button size="small" :disabled="selectedRowsCount === 0" @click="handleSelectNone">{{ t('message.pages.menu.buttons.selectNone') }}</el-button>
			<el-divider direction="vertical" />
			<el-button size="small" type="danger" plain :icon="Delete" :disabled="selectedRowsCount === 0" @click="handleBatchDelete">
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
import { computed, nextTick, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useFs } from '@fast-crud/fast-crud';
import { createCrudOptions } from './crud';
import { MenuTreeItemType } from '../../types';
import { ElMessage, ElMessageBox } from 'element-plus';
import XEUtils from 'xe-utils';
import { BatchDelete } from './api';
import { Delete, Check } from '@element-plus/icons-vue';
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

// 是否有数据可选择
const isSelectable = computed(() => {
	return totalCount.value > 0 && context!.selectOptions.value?.id != null;
});

// 总条数
const totalCount = computed(() => {
	return crudBinding.value?.pagination?.total || 0;
});

// 全选
const handleSelectAll = () => {
	const tableRef = crudExpose.getBaseTableRef();
	const tableData = crudExpose.getTableData();
	nextTick(() => {
		tableRef.toggleAllSelection();
		selectedRows.value = [...tableData];
	});
};

// 取消全选
const handleSelectNone = () => {
	const tableRef = crudExpose.getBaseTableRef();
	tableRef.clearSelection();
	selectedRows.value = [];
};

// 批量删除
const handleBatchDelete = async () => {
	await ElMessageBox.confirm(
		t('message.pages.menu.messages.batchDeleteConfirm', { count: selectedRows.value.length }),
		t('message.pages.menu.buttons.confirm'),
		{ distinguishCancelAndClose: true, confirmButtonText: t('message.pages.menu.buttons.confirm'), cancelButtonText: t('message.pages.menu.buttons.cancel'), closeOnClickModal: false, type: 'warning' }
	);
	// 先拿到 ids，再清空
	const ids = XEUtils.pluck(selectedRows.value, 'id');
	const tableRef = crudExpose.getBaseTableRef();
	tableRef.clearSelection();
	selectedRows.value = [];
	await BatchDelete(ids);
	ElMessage.success(t('message.pages.menu.messages.deleteSuccess'));
	await crudExpose.doRefresh();
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
