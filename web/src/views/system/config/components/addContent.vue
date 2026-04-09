<template>
	<div style="padding: 20px">
		<el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
			<el-form-item :label="t('message.pages.config.form.parent')" prop="parent">
				<el-select v-model="form.parent" :placeholder="t('message.pages.config.form.parentPlaceholder')" clearable>
					<el-option :label="item.title" :value="item.id" :key="index" v-for="(item, index) in parentOptions"></el-option>
				</el-select>
			</el-form-item>
			<el-form-item :label="t('message.pages.config.form.title')" prop="title">
				<el-input v-model="form.title" :placeholder="t('message.pages.config.form.titlePlaceholder')" clearable></el-input>
			</el-form-item>
			<el-form-item :label="t('message.pages.config.form.key')" prop="key">
				<el-input v-model="form.key" :placeholder="t('message.pages.config.form.keyPlaceholder')" clearable></el-input>
			</el-form-item>
			<el-form-item :label="t('message.pages.config.form.formItemType')" prop="form_item_type">
				<el-select v-model="form.form_item_type" :placeholder="t('message.pages.config.form.formItemTypePlaceholder')" clearable>
					<el-option :label="item.label" :value="item.value" :key="index" v-for="(item, index) in dictionary('config_form_type')"></el-option>
				</el-select>
			</el-form-item>
			<el-form-item
				v-if="[4, 5, 6].indexOf(form.form_item_type) > -1"
				:label="t('message.pages.config.form.dictKey')"
				prop="setting"
				:rules="[{ required: true, message: t('message.pages.config.validation.dictKeyRequired') }]"
			>
				<el-input v-model="form.setting" :placeholder="t('message.pages.config.form.dictKeyPlaceholder')" clearable></el-input>
			</el-form-item>
			<div v-if="[13, 14].indexOf(form.form_item_type) > -1">
				<associationTable ref="associationTableRef" v-model="form.setting" @updateVal="associationTableUpdate"></associationTable>
			</div>
			<el-form-item :label="t('message.pages.config.form.validationRule')">
				<el-select v-model="form.rule" multiple :placeholder="t('message.pages.config.form.validationRulePlaceholder')" clearable>
					<el-option :label="item.label" :value="item.value" :key="index" v-for="(item, index) in ruleOptions"></el-option>
				</el-select>
			</el-form-item>
			<el-form-item :label="t('message.pages.config.form.placeholder')" prop="placeholder">
				<el-input v-model="form.placeholder" :placeholder="t('message.pages.config.form.placeholderPlaceholder')" clearable></el-input>
			</el-form-item>
			<el-form-item :label="t('message.pages.config.form.sort')" prop="sort">
				<el-input-number v-model="form.sort" :min="0" :max="99"></el-input-number>
			</el-form-item>
			<el-form-item>
				<el-button type="primary" @click="onSubmit(formRef)">{{ t('message.pages.config.buttons.createNow') }}</el-button>
			</el-form-item>
		</el-form>
	</div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import * as api from '../api';
import associationTable from './components/associationTable.vue';
import { ref, reactive, onMounted, inject } from 'vue';
import type { FormInstance, FormRules } from 'element-plus';
import { successMessage } from '/@/utils/message';
import { dictionary } from '/@/utils/dictionary';

const { t } = useI18n();

let form: any = reactive({
	parent: null,
	title: null,
	key: null,
	form_item_type: '',
	rule: null,
	placeholder: null,
});
const formRef = ref<FormInstance>();
const associationTableRef: any = ref<FormInstance>();
const rules = reactive<FormRules>({
	parent: [
		{
			required: true,
			message: t('message.pages.config.validation.parentRequired'),
		},
	],
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
			pattern: /^[A-Za-z0-9_]+$/,
			message: t('message.pages.config.validation.keyFormat2'),
		},
	],
	form_item_type: [
		{
			required: true,
			message: t('message.pages.config.validation.formItemTypeRequired'),
		},
	],
});
let parentOptions: any = ref([]);
let ruleOptions = ref([
	{
		label: t('message.pages.config.validationRules.required'),
		value: '{"required": true, "message": "必填项不能为空"}',
	},
	{
		label: t('message.pages.config.validationRules.email'),
		value: '{ "type": "email", "message": "请输入正确的邮箱地址"}',
	},
	{
		label: t('message.pages.config.validationRules.url'),
		value: '{ "type": "url", "message": "请输入正确的URL地址"}',
	},
]);
const getParent = () => {
	api
		.GetList({
			parent__isnull: true,
			limit: 999,
		})
		.then((res: any) => {
			parentOptions.value = res.data;
		});
};

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

// 关联表数据更新
const associationTableUpdate = () => {
	return new Promise(function (resolve, reject) {
		if (associationTableRef) {
			if (!associationTableRef.onSubmit()) {
				// eslint-disable-next-line prefer-promise-reject-errors
				return reject(false);
			}
			const { formObj } = associationTableRef;
			form.setting = formObj;
			return resolve(true);
		} else {
			return resolve(true);
		}
	});
};

onMounted(() => {
	getParent();
});
</script>

<style></style>
