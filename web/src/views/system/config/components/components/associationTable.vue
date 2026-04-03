<template>
	<div>
		<el-form :model="formObj" ref="associationRef">
			<el-form-item label="关联表" prop="table" :rules="[{ required: true, message: '必填项', trigger: 'blur' }]">
				<el-select v-model="formObj.table" filterable clearable placeholder="请选择" @change="handleChange">
					<el-option v-for="item in tableOptions" :key="item.table" :label="item.tableName" :value="item.table">
						<span style="float: left">{{ item.tableName }}</span>
						<span style="float: right; color: #8492a6; font-size: 13px">{{ item.table }}</span>
					</el-option>
				</el-select>
			</el-form-item>
			<el-form-item label="显示字段" prop="field" :rules="[{ required: true, message: '必填项', trigger: 'blur' }]">
				<el-select v-model="formObj.field" filterable clearable placeholder="请选择">
					<el-option v-for="item in labelOptions" :key="item.table" :label="item.title" :value="item.field">
						<span style="float: left">{{ item.field }}</span>
						<span style="float: right; color: #8492a6; font-size: 13px">{{ item.title }}</span>
					</el-option>
				</el-select>
			</el-form-item>
			<el-form-item label="储存字段" prop="primarykey" :rules="[{ required: true, message: '必填项', trigger: 'blur' }]">
				<el-select v-model="formObj.primarykey" filterable clearable placeholder="请选择">
					<el-option v-for="(item, index) in labelOptions" :key="index" :label="item.title" :value="item.field">
						<span style="float: left">{{ item.field }}</span>
						<span style="float: right; color: #8492a6; font-size: 13px">{{ item.title }}</span>
					</el-option>
				</el-select>
			</el-form-item>
			<el-form-item label="过滤条件" prop="oldSearchField" :rules="[{ required: true, message: '必填项', trigger: 'blur' }]">
				<el-select v-model="formObj.oldSearchField" multiple filterable clearable placeholder="请选择" @change="handleSearch">
					<el-option v-for="(item, index) in labelOptions" :key="index" :label="item.title" :value="item.field">
						<span style="float: left">{{ item.field }}</span>
						<span style="float: right; color: #8492a6; font-size: 13px">{{ item.title }}</span>
					</el-option>
				</el-select>
			</el-form-item>
		</el-form>
	</div>
</template>

<script setup lang="ts">
import * as api from '../../api';
import { ref, reactive, onMounted } from 'vue';
import type { FormInstance, FormRules } from 'element-plus';
import { successMessage } from '/@/utils/message';
let formObj: any = reactive({
	table: null,
	primarykey: null,
	field: null,
	searchField: null,
	oldSearchField: null,
});
let searchField = ref('');
let tableOptions: any = ref([]);
let labelOptions: any = ref([]);
const associationRef: any = ref<FormInstance>();

const emits = defineEmits(['updateVal']);
const props = defineProps(['value']);
// 初始化数据
const init = () => {
	api.GetAssociationTable().then((res: any) => {
		const { data } = res.data;
		tableOptions = data;
		// 设置默认选中
		formObj.table = data[0].table;
		labelOptions = data[0].tableFields;
		formObj.primarykey = 'id';
		formObj.field = 'id';
	});
};
// 选中事件
const handleChange = (val: any) => {
	const { tableFields } = tableOptions.find((item: any) => {
		return item.table === val;
	});
	labelOptions = tableFields;
};

// 过滤条件选中
const handleSearch = (val: any) => {
	const fields = labelOptions.filter((item: any) => {
		return val.indexOf(item.field) > -1;
	});
	formObj.searchField = fields;
};
// 更新数据
const handleUpdate = () => {
	emits('updateVal', formObj);
};
// 数据验证
const onSubmit = () => {
	let res = false;
	associationRef.value.validate((valid: any) => {
		if (valid) {
			res = true;
		} else {
			return false;
		}
	});
	return res;
};
</script>

<style></style>
