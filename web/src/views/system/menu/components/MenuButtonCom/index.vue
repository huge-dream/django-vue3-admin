<template>
	<div style="height: 100%">
		<fs-crud ref="crudRef" v-bind="crudBinding" style="height: 100%">
			<template #pagination-left>
				<el-tooltip :content="t('message.pages.menu.buttons.batchDelete')">
					<el-button text type="danger" :disabled="selectedRowsCount === 0" :icon="Delete" circle @click="handleBatchDelete" />
				</el-tooltip>
			</template>
			<template #pagination-right>
				<el-popover placement="top" :width="400" trigger="click">
					<template #reference>
						<el-button text :type="selectedRowsCount > 0 ? 'primary' : ''">
							{{ t('message.pages.menu.buttons.selectedCount', { count: selectedRowsCount }) }}
						</el-button>
					</template>
					<el-table :data="selectedRows" size="small" max-height="300">
						<el-table-column width="150" property="id" label="ID" />
						<el-table-column width="200" property="name" label="name" />
						<el-table-column fixed="right" :label="t('message.pages.menu.table.columns.actions')" width="60">
							<template #default="scope">
								<el-button text type="info" :icon="Close" @click="removeSelectedRows(scope.row)" circle />
							</template>
						</el-table-column>
					</el-table>
				</el-popover>
			</template>
		</fs-crud>
	</div>
</template>

<script lang="ts" setup>
import { ref, onMounted, reactive, computed, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useFs } from '@fast-crud/fast-crud';
import { createCrudOptions } from './crud';
import { MenuTreeItemType } from '../../types';
import { ElMessage, ElMessageBox } from 'element-plus';
import XEUtils from 'xe-utils';
import { BatchDelete } from './api';
import { Close, Delete } from '@element-plus/icons-vue';
import { useThemeConfig } from '/@/stores/themeConfig';
import { storeToRefs } from 'pinia';

const { themeConfig } = storeToRefs(useThemeConfig());

const { t } = useI18n();

let selectOptions: any = ref({ name: null });

const { crudRef, crudBinding, crudExpose, selectedRows, resetCrudOptions } = useFs({ createCrudOptions, context: { selectOptions } });
const { doRefresh, setTableData } = crudExpose;

// 选中行的条数
const selectedRowsCount = computed(() => {
	return selectedRows.value.length;
});

// 批量删除
const handleBatchDelete = async () => {
	await ElMessageBox.confirm(
		t('message.pages.menu.messages.batchDeleteConfirm', { count: selectedRows.value.length }),
		t('message.pages.menu.buttons.confirm'),
		{ distinguishCancelAndClose: true, confirmButtonText: t('message.pages.menu.buttons.confirm'), cancelButtonText: t('message.pages.menu.buttons.cancel'), closeOnClickModal: false, type: 'warning' }
	);
	await BatchDelete(XEUtils.pluck(selectedRows.value, 'id'));
	selectedRows.value = [];
	await crudExpose.doRefresh();
	ElMessage.success(t('message.pages.menu.messages.deleteSuccess'));
};

// 移除已选中的行
const removeSelectedRows = (row: any) => {
	const tableRef = crudExpose.getBaseTableRef();
	const tableData = crudExpose.getTableData();
	if (XEUtils.pluck(tableData, 'id').includes(row.id)) {
		tableRef.toggleRowSelection(row, false);
	} else {
		selectedRows.value = XEUtils.remove(selectedRows.value, (item: any) => item.id !== row.id);
	}
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
