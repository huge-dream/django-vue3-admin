<template>
	<fs-crud ref="crudRef"  v-bind="crudBinding"> 
		<template #pagination-left>
				<el-tooltip content="批量删除">
					<el-button text type="danger" :disabled="selectedRowsCount === 0" :icon="Delete" circle @click="handleBatchDelete" />
				</el-tooltip>
			</template>
			<template #pagination-right>
				<el-popover placement="top" :width="400" trigger="click">
					<template #reference>
						<el-button text :type="selectedRowsCount > 0 ? 'primary' : ''">已选中{{ selectedRowsCount }}条数据</el-button>
					</template>
					<el-table :data="selectedRows" size="small">
						<el-table-column width="150" property="id" label="id" />
						<el-table-column fixed="right" label="操作" min-width="60">
							<template #default="scope">
								<el-button text type="info" :icon="Close" @click="removeSelectedRows(scope.row)" circle />
							</template>
						</el-table-column>
					</el-table>
				</el-popover>
			</template>
	</fs-crud>
</template>

<script lang="ts" setup>
import { computed, ref } from 'vue';
import { useFs } from '@fast-crud/fast-crud';
import { createCrudOptions } from './crud';
import { MenuTreeItemType } from '../../types';
import { ElMessage, ElMessageBox } from 'element-plus';
import XEUtils from 'xe-utils';
import { BatchDelete } from './api';
import { Close, Delete } from '@element-plus/icons-vue';
// 当前选择的菜单信息
let selectOptions: any = ref({ name: null });

const { crudRef, crudBinding, crudExpose, context,selectedRows } = useFs({ createCrudOptions, context: { selectOptions } });
const { doRefresh, setTableData } = crudExpose;

// 选中行的条数
const selectedRowsCount = computed(() => {
	return selectedRows.value.length;
});

// 批量删除
const handleBatchDelete = async () => {
	await ElMessageBox.confirm(`确定要批量删除这${selectedRows.value.length}条记录吗`, '确认', {
		distinguishCancelAndClose: true,
		confirmButtonText: '确定',
		cancelButtonText: '取消',
		closeOnClickModal: false,
	});
	await BatchDelete(XEUtils.pluck(selectedRows.value, 'id'));
	ElMessage.info('删除成功');
	selectedRows.value = [];
	await crudExpose.doRefresh();
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
		//清空表格数据
		setTableData([]);
	}
};

defineExpose({ selectOptions, handleRefreshTable });
</script>
