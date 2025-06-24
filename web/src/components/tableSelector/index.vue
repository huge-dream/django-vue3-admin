<template>
	<el-select
		popper-class="popperClass"
		class="tableSelector"
		multiple
    :collapseTags="props.tableConfig.collapseTags"
		v-model="data"
		placeholder="请选择"
		@visible-change="visibleChange"
	>
		<template #empty>
			<div class="option">
				<el-input style="margin-bottom: 10px" v-model="search" clearable placeholder="请输入关键词" @change="getDict" @clear="getDict">
					<template #append>
						<el-button type="primary" icon="Search" />
					</template>
				</el-input>
				<el-table
					ref="tableRef"
					:data="tableData"
					:size="props.tableConfig.size"
					border
					row-key="id"
					:lazy="props.tableConfig.lazy"
					:load="props.tableConfig.load"
					:tree-props="props.tableConfig.treeProps"
					style="width: 600px"
					max-height="200"
					height="200"
					:highlight-current-row="!props.tableConfig.isMultiple"
					@selection-change="handleSelectionChange"
					@select="handleSelectionChange"
					@selectAll="handleSelectionChange"
					@current-change="handleCurrentChange"
				>
					<el-table-column v-if="props.tableConfig.isMultiple" fixed type="selection" reserve-selection width="55" />
					<el-table-column fixed type="index" label="#" width="50" />
					<el-table-column
						:prop="item.prop"
						:label="item.label"
						:width="item.width"
						v-for="(item, index) in props.tableConfig.columns"
						:key="index"
					/>
				</el-table>
				<el-pagination
					style="margin-top: 10px"
					background
					v-model:current-page="pageConfig.page"
					v-model:page-size="pageConfig.limit"
					layout="prev, pager, next"
					:total="pageConfig.total"
					@current-change="handlePageChange"
				/>
			</div>
		</template>
	</el-select>
</template>

<script setup lang="ts">
import { computed, defineProps, onMounted, reactive, ref, watch } from 'vue';
import XEUtils from 'xe-utils';
import { request } from '/@/utils/service';

const props = defineProps({
	modelValue: {
		type: Array || String || Number,
		default: () => [],
	},
	tableConfig: {
		type: Object,
		default: {
			url: null,
			label: null, //显示值
			value: null, //数据值
			isTree: false,
			lazy: true,
			size: 'default',
			load: () => {},
			data: [], //默认数据
			isMultiple: false, //是否多选
			collapseTags: false,
			treeProps: { children: 'children', hasChildren: 'hasChildren' },
			columns: [], //每一项对应的列表项
		},
	},
	displayLabel: {},
} as any);
console.log(props.tableConfig);

const emit = defineEmits(['update:modelValue']);
// tableRef
const tableRef = ref();
// template上使用data
const data = ref();
// 多选值
const multipleSelection = ref();
// 搜索值
const search = ref(undefined);
//表格数据
const tableData = ref([]);
// 分页的配置
const pageConfig = reactive({
	page: 1,
	limit: 10,
	total: 0,
});

/**
 * 表格多选
 * @param val:Array
 */
const handleSelectionChange = (val: any) => {
	const { tableConfig } = props;
	const result = val.map((item: any) => {
		return item[tableConfig.value];
	});
	data.value = val.map((item: any) => {
		return item[tableConfig.label];
	});

	emit('update:modelValue', result);
};
/**
 * 表格单选
 * @param val:Object
 */
const handleCurrentChange = (val: any) => {
	const { tableConfig } = props;
	if (!tableConfig.isMultiple && val) {
		// data.value = [val[tableConfig.label]];
		emit('update:modelValue', val[tableConfig.value]);
	}
};

/**
 * 获取字典值
 */
const getDict = async () => {
	const url = props.tableConfig.url;
	console.log(url);

	const params = {
		page: pageConfig.page,
		limit: pageConfig.limit,
		search: search.value,
	};
	const { data, page, limit, total } = await request({
		url: url,
		params: params,
	});
	pageConfig.page = page;
	pageConfig.limit = limit;
	pageConfig.total = total;
	if (props.tableConfig.data === undefined || props.tableConfig.data.length === 0) {
		if (props.tableConfig.isTree) {
			tableData.value = XEUtils.toArrayTree(data, { parentKey: 'parent', key: 'id', children: 'children' });
		} else {
			tableData.value = data;
		}
	} else {
		tableData.value = props.tableConfig.data;
	}
};

// 获取节点值
const getNodeValues = () => {
	console.log(props.tableConfig.url);
	
	request({
		url: props.tableConfig.url,
		method: 'post',
		data: { ids: props.modelValue },
	}).then((res) => {
		if (res.data.length > 0) {
			data.value = res.data.map((item: any) => {
				return item[props.tableConfig.label];
			});

			tableRef.value!.clearSelection();
			res.data.forEach((row) => {
				tableRef.value!.toggleRowSelection(row, true, false);
			});
		}
	});
};

/**
 * 下拉框展开/关闭
 * @param bool
 */
const visibleChange = (bool: any) => {
	if (bool) {
		getDict();
	}
};

/**
 * 分页
 * @param page
 */
const handlePageChange = (page: any) => {
	pageConfig.page = page;
	getDict();
};

onMounted(() => {
	// setTimeout(() => {
	// 	getNodeValues();
	// }, 1000);
});
</script>

<style scoped>
.option {
	height: auto;
	line-height: 1;
	padding: 5px;
	background-color: #fff;
}
</style>
<style lang="scss">
.popperClass {
	height: 320px;
}

.el-select-dropdown__wrap {
	max-height: 310px !important;
}

.tableSelector {
	.el-icon,
	.el-tag__close {
		display: none;
	}
}
</style>
