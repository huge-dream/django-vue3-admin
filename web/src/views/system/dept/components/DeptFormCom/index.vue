<template>
	<el-form ref="formRef" :rules="rules" :model="deptFormData" label-width="100px" label-position="right" class="dept-form-com">
		<el-form-item label="父级部门" prop="parent">
			<el-tree-select
				v-model="deptFormData.parent"
				:props="defaultTreeProps"
				:data="deptDefaultList"
				:cache-data="props.cacheData"
				lazy
				check-strictly
				:load="handleTreeLoad"
				style="width: 100%"
			/>
		</el-form-item>
		<el-form-item required label="部门名称" prop="name">
			<el-input v-model="deptFormData.name" />
		</el-form-item>
		<el-form-item required label="部门标识" prop="key">
			<el-input v-model="deptFormData.key" />
		</el-form-item>
		<el-form-item label="负责人">
			<el-input v-model="deptFormData.owner" placeholder="请输入" />
		</el-form-item>
		<el-form-item label="备注">
			<el-input v-model="deptFormData.description" maxlength="200" show-word-limit type="textarea" />
		</el-form-item>
		<el-form-item>
			<el-button @click="handleUpdateMenu" type="primary" :loading="deptBtnLoading">
				{{ deptFormData.id ? '保存' : '新增' }}
			</el-button>
			<el-button @click="handleClose">取消 </el-button>
		</el-form-item>
	</el-form>
</template>

<script lang="ts" setup>
import { reactive, ref, onMounted } from 'vue';
import { ElForm, FormRules } from 'element-plus';
import { lazyLoadDept, AddObj, UpdateObj } from '../../api';
import { successNotification } from '/@/utils/message';
import { DeptFormDataType, TreeItemType, APIResponseData } from '../../types';
import type Node from 'element-plus/es/components/tree/src/model/node';

interface IProps {
	initFormData: TreeItemType | null;
	treeData: TreeItemType[];
	cacheData: TreeItemType[];
}

const defaultTreeProps: any = {
	children: 'children',
	label: 'name',
	value: 'id',
	isLeaf: (data: TreeItemType[], node: Node) => {
		if (node?.data.hasChild) {
			return false;
		} else {
			return true;
		}
	},
};

const formRef = ref<InstanceType<typeof ElForm>>();
const rules = reactive<FormRules>({
	name: [{ required: true, message: '部门名称必填', trigger: 'blur' }],
	key: [{ required: true, message: '部门标识必填', trigger: 'blur' }],
});

const props = withDefaults(defineProps<IProps>(), {
	initFormData: () => null,
	treeData: () => [],
	cacheData: () => [],
});
const emit = defineEmits(['drawerClose']);

let deptDefaultList = ref<TreeItemType[]>([]);
let deptFormData = reactive<DeptFormDataType>({
	key: '',
	parent: '',
	name: '',
	owner: '',
	description: '',
});
let deptBtnLoading = ref(false);

const setDeptFormData = () => {
	if (props.initFormData?.id) {
		deptFormData.id = props.initFormData?.id;
		deptFormData.key = props.initFormData.key || '';
		deptFormData.parent = props.initFormData.parent || '';
		deptFormData.name = props.initFormData.name || '';
		deptFormData.owner = props.initFormData.owner || '';
		deptFormData.description = props.initFormData.description || '';
	}
};

const handleTreeLoad = (node: Node, resolve: Function) => {
	if (node.level !== 0) {
		lazyLoadDept({ parent: node.data.id }).then((res: APIResponseData) => {
			resolve(res.data);
		});
	}
};

const handleUpdateMenu = () => {
	formRef.value?.validate(async (valid) => {
		if (!valid) return;
		try {
			let res;
			deptBtnLoading.value = true;
			if (deptFormData.id) {
				res = await UpdateObj(deptFormData);
			} else {
				res = await AddObj(deptFormData);
			}
			if (res?.code === 2000) {
				successNotification(res.msg as string);
				handleClose('submit');
			}
		} finally {
			deptBtnLoading.value = false;
		}
	});
};

const handleClose = (type: string = '') => {
	emit('drawerClose', type);
	formRef.value?.resetFields();
};

onMounted(async () => {
	props.treeData.map((item) => {
		deptDefaultList.value.push(item);
	});
	setDeptFormData();
});
</script>

<style lang="scss" scoped>
.dept-form-com {
	height: 100%;
	padding: 20px;
	box-sizing: border-box;
}
</style>
