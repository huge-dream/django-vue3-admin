<template>
	<div>
		<el-dialog ref="modelRef" v-model="modelDialog" title="选择model">
			<div v-show="props.model">
				<el-tag>已选择:{{ props.model }}</el-tag>
			</div>
			<!-- 搜索输入框 -->
			<el-input v-model="searchQuery" placeholder="搜索模型..." style="margin-bottom: 10px"></el-input>
			<div class="model-card">
				<!--注释编号:django-vue3-admin-index483211: 对请求回来的allModelData进行computed计算，返加搜索框匹配到的内容-->
				<div v-for="(item, index) in filteredModelData" :value="item.key" :key="index">
					<el-text :type="modelCheckIndex === index ? 'primary' : ''" @click="onModelChecked(item, index)">
						{{ item.app + '--' + item.title + '(' + item.key + ')' }}
					</el-text>
				</div>
			</div>
			<template #footer>
				<span class="dialog-footer">
					<el-button @click="modelDialog = false">取消</el-button>
					<el-button type="primary" @click="handleAutomatch"> 确定 </el-button>
				</span>
			</template>
		</el-dialog>
		<div style="height: 72vh">
			<fs-crud ref="crudRef" v-bind="crudBinding">
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
		</div>
	</div>
</template>

<script lang="ts" setup>
import { ref, onMounted, reactive, computed } from 'vue';
import { useFs } from '@fast-crud/fast-crud';
import { createCrudOptions } from './crud';
import { BatchDelete, getModelList } from './api';
import { Close, Delete } from '@element-plus/icons-vue';
import { MenuTreeItemType } from '/@/views/system/menu/types';
import { successMessage, successNotification, warningNotification } from '/@/utils/message';
import { automatchColumnsData } from '/@/views/system/columns/components/ColumnsTableCom/api';
import XEUtils from 'xe-utils';
import { ElMessage, ElMessageBox } from 'element-plus';
// 当前选择的菜单信息
let selectOptions: any = ref({ name: null });

const props = reactive({
	model: '',
	app: '',
	menu: '',
});

//model弹窗
const modelDialog = ref(false);
// 获取所有model
const allModelData = ref<any[]>([]);
const modelCheckIndex = ref(null);
const onModelChecked = (row, index) => {
	modelCheckIndex.value = index;
	props.model = row.key;
	props.app = row.app;
};

// 注释编号:django-vue3-admin-index083311:代码开始行
// 功能说明:搭配搜索的处理，返回搜索结果
const searchQuery = ref('');

const filteredModelData = computed(() => {
	if (!searchQuery.value) {
		return allModelData.value;
	}
	const query = searchQuery.value.toLowerCase();
	return allModelData.value.filter(
		(item) => item.app.toLowerCase().includes(query) || item.title.toLowerCase().includes(query) || item.key.toLowerCase().includes(query)
	);
});
// 注释编号:django-vue3-admin-index083311:代码结束行

/**
 * 菜单选中时,加载表格数据
 * @param record
 */
const handleRefreshTable = (record: MenuTreeItemType) => {
	if (!record.is_catalog && record.id) {
		selectOptions.value = record;
		crudExpose.doRefresh();
	} else {
		//清空表格数据
		crudExpose.setTableData([]);
	}
};
/**
 * 自动匹配列
 */
const handleAutomatch = async () => {
	props.menu = selectOptions.value.id;
	modelDialog.value = false;
	if (props.menu && props.model) {
		const res = await automatchColumnsData(props);
		if (res?.code === 2000) {
			successNotification('匹配成功');
		}
		crudExpose.doSearch({ form: { menu: props.menu, model: props.model } });
	} else {
		warningNotification('请选择角色和模型表！');
	}
};

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

const { crudBinding, crudRef, crudExpose, selectedRows } = useFs({ createCrudOptions, props, modelDialog, selectOptions, allModelData });
onMounted(async () => {
	const res = await getModelList();
	allModelData.value = res.data;
});

defineExpose({ selectOptions, handleRefreshTable });
</script>

<style scoped lang="scss">
.model-card {
	margin-top: 10px;
	height: 30vh;
	overflow-y: scroll;

	div {
		margin: 15px 0;
		cursor: pointer;
	}
}
</style>
