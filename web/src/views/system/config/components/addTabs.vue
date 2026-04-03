<template>
	<div style="padding: 20px">
		<el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
			<el-form-item label="标题" prop="title">
				<el-input v-model="form.title"></el-input>
			</el-form-item>
			<el-form-item label="key值" prop="key">
				<el-input v-model="form.key"></el-input>
			</el-form-item>
			<el-form-item>
				<el-button type="primary" @click="onSubmit(formRef)">立即创建</el-button>
				<el-button>取消</el-button>
			</el-form-item>
		</el-form>
	</div>
</template>

<script setup lang="ts">
import * as api from '../api';
import {ref, reactive, inject} from 'vue';
import type { FormInstance, FormRules } from 'element-plus';
import { successMessage } from '/@/utils/message';

let form = reactive({
	title: null,
	key: null,
});
const formRef = ref<FormInstance>();
const rules = reactive<FormRules>({
	title: [
		{
			required: true,
			message: '请输入',
		},
	],
	key: [
		{
			required: true,
			message: '请输入',
		},
		{
			pattern: /^[A-Za-z0-9]+$/,
			message: '只能是英文和数字',
		},
	],
});


const refreshView:any = inject('refreshView')
const onSubmit = async (formEl: FormInstance | undefined) => {
	if (!formEl) return;
	await formEl.validate((valid, fields) => {
		if (valid) {
			api.AddObj(form).then((res: any) => {
				if (res.code == 2000) {
          successMessage('新增成功');
          refreshView()
        }

			});
		} else {
			console.log('error submit!', fields);
		}
	});
};
</script>

<style></style>
