<template>
	<el-dialog v-model="dialog" title="添加授权用户" direction="rtl" destroy-on-close :before-close="handleDialogClose">
		<div style="height: 500px;" >
			<fs-crud ref="crudRef" v-bind="crudBinding">
				<template #pagination-right>
					<el-popover placement="top" :width="200" trigger="click">
						<template #reference>
							<el-button text :type="selectedRowsCount > 0 ? 'primary' : ''">已选中{{ selectedRowsCount }}条数据</el-button>
						</template>
						<el-table :data="selectedRows" size="small" :max-height="500">
							<!-- <el-table-column width="100" property="id" label="id" /> -->
							<el-table-column width="100" property="name" label="用户名" />
							<el-table-column fixed="right" label="操作" min-width="50">
								<template #default="scope">
									<el-button text type="info" :icon="Close" @click="removeSelectedRows(scope.row)" circle />
								</template>
							</el-table-column>
						</el-table>
					</el-popover>
				</template>

			</fs-crud>
		</div>
		<template #footer>
			<div>
				<el-button type="primary" @click="handleDialogConfirm"> 确定</el-button>
				<el-button @click="handleDialogClose"> 取消</el-button>
			</div>
		</template>
	</el-dialog>
</template>

<script lang="ts" setup>
import { ref, computed } from 'vue';
import { useFs } from '@fast-crud/fast-crud';
import { createCrudOptions } from './crud';
import { successNotification } from '/@/utils/message';
import { addRoleUsers } from './api';
import { Close } from '@element-plus/icons-vue';
import XEUtils from 'xe-utils';

const props = defineProps({
  refreshCallback: {
    type: Function,
    required: true,
  },
});

//对话框是否显示
const dialog = ref(false);

// 父组件刷新回调函数
const parentRefreshCallbackFunc =  props.refreshCallback;

//抽屉关闭确认
const handleDialogClose = () => {
	dialog.value = false;
	selectedRows.value = [];
};

const handleDialogConfirm = async () => {
	if (selectedRows.value.length === 0) {
		return;
	}
	await addRoleUsers(crudRef.value.getSearchFormData().role_id, XEUtils.pluck(selectedRows.value, 'id')).then(res => {
		successNotification(res.msg);
	})
	parentRefreshCallbackFunc && parentRefreshCallbackFunc();  // 刷新父组件
	handleDialogClose();
};

const { crudBinding, crudRef, crudExpose, selectedRows } = useFs({ createCrudOptions, context: {} });
const { setSearchFormData, doRefresh } = crudExpose;

// 选中行的条数
const selectedRowsCount = computed(() => {
	return selectedRows.value.length;
});

const removeSelectedRows = (row: any) => {
	const tableRef = crudExpose.getBaseTableRef();
	const tableData = crudExpose.getTableData();
	if (XEUtils.pluck(tableData, 'id').includes(row.id)) {
		tableRef.toggleRowSelection(row, false);
	} else {
		selectedRows.value = XEUtils.remove(selectedRows.value, (item: any) => item.id !== row.id);
	}
};

defineExpose({ dialog, setSearchFormData, doRefresh, parentRefreshCallbackFunc});
</script>
