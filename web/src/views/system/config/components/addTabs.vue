<template>
	<div style="padding: 20px">
		<el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
			<el-form-item :label="t('message.pages.config.form.title')" prop="title">
				<el-input v-model="form.title"></el-input>
			</el-form-item>
			<el-form-item :label="t('message.pages.config.form.key')" prop="key">
				<el-input v-model="form.key"></el-input>
			</el-form-item>
			<el-form-item>
				<el-button type="primary" @click="onSubmit(formRef)">{{ t('message.pages.config.buttons.createNow') }}</el-button>
				<el-button>{{ t('message.pages.config.buttons.cancel') }}</el-button>
			</el-form-item>
		</el-form>
	</div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import * as api from '../api';
import { ref, reactive, inject } from 'vue';
import type { FormInstance, FormRules } from 'element-plus';
import { successMessage } from '/@/utils/message';

const { t } = useI18n();

let form = reactive({
	title: null,
	key: null,
});
const formRef = ref<FormInstance>();
const rules = reactive<FormRules>({
	title: [
		{
			required: true,
			message: t('message.pages.config.validation.titleRequired'),
		},
	],
	key: [
		{
			required: true,
			message: t('message.pages.config.validation.keyRequired'),
		},
		{
			pattern: /^[A-Za-z0-9]+$/,
			message: t('message.pages.config.validation.keyFormat'),
		},
	],
});

const refreshView: any = inject('refreshView');
const onSubmit = async (formEl: FormInstance | undefined) => {
	if (!formEl) return;
	await formEl.validate((valid, fields) => {
		if (valid) {
			api.AddObj(form).then((res: any) => {
				if (res.code == 2000) {
					successMessage(t('message.pages.config.messages.addSuccess'));
					refreshView();
				}
			});
		} else {
			console.log('error submit!', fields);
		}
	});
};
</script>

<style></style>
