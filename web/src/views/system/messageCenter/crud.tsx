import * as api from './api';
import { useI18n } from 'vue-i18n';
import { dict, useCompute, PageQuery, AddReq, DelReq, EditReq, CreateCrudOptionsProps, CreateCrudOptionsRet } from '@fast-crud/fast-crud';
import tableSelector from '/@/components/tableSelector/index.vue';
import { shallowRef, computed } from 'vue';
import manyToMany from '/@/components/manyToMany/index.vue';
import { auth } from '/@/utils/authFunction';
const { compute } = useCompute();

export default function ({ crudExpose, context }: CreateCrudOptionsProps): CreateCrudOptionsRet {
	const { t } = useI18n()
	const { tabActivted } = context; //从context中获取tabActivted

	const pageRequest = async (query: PageQuery) => {
		if (tabActivted.value === 'receive') {
			return await api.GetSelfReceive(query);
		}
		return await api.GetList(query);
	};
	const editRequest = async ({ form, row }: EditReq) => {
		form.id = row.id;
		return await api.UpdateObj(form);
	};
	const delRequest = async ({ row }: DelReq) => {
		return await api.DelObj(row.id);
	};
	const addRequest = async ({ form }: AddReq) => {
		return await api.AddObj(form);
	};

	const viewRequest = async ({ row }: { row: any }) => {
		return await api.GetObj(row.id);
	};

	const IsReadFunc = computed(() => {
		return tabActivted.value === 'receive';
	});

	return {
		crudOptions: {
			request: {
				pageRequest,
				addRequest,
				editRequest,
				delRequest,
			},
			actionbar: {
				buttons: {
					add: {
						show: computed(() => {
							return tabActivted.value !== 'receive' && auth('messageCenter:Create');
						}),
					},
				},
			},
			rowHandle: {
				fixed: 'right',
				width: 180,
				buttons: {
					edit: {
						show: false,
					},
					view: {
						text: t('message.pages.messageCenter.buttons.view'),
						type: 'text',
						iconRight: 'View',
						show: auth('messageCenter:Search'),
						click({ index, row }) {
							crudExpose.openView({ index, row });
							if (tabActivted.value === 'receive') {
								viewRequest({ row });
								crudExpose.doRefresh();
							}
						},
					},
					remove: {
						iconRight: 'Delete',
						type: 'text',
						show: auth('messageCenter:Delete'),
					},
				},
			},
			columns: {
				id: {
					title: 'id',
					form: {
						show: false,
					},
				},
				title: {
					title: t('message.pages.messageCenter.table.columns.title'),
					search: {
						show: true,
					},
					type: ['text', 'colspan'],
					column: {
						minWidth: 120,
					},
					form: {
						rules: [
							// 表单校验规则
							{
								required: true,
								message: t('message.pages.messageCenter.validation.titleRequired'),
							},
						],
						component: { span: 24, placeholder: t('message.pages.messageCenter.form.titlePlaceholder') },
					},
				},
				is_read: {
					title: t('message.pages.messageCenter.table.columns.isRead'),
					type: 'dict-select',
					column: {
						show: IsReadFunc.value,
					},
					dict: dict({
						data: [
							{ label: t('message.pages.messageCenter.status.yes'), value: true, color: 'success' },
							{ label: t('message.pages.messageCenter.status.no'), value: false, color: 'danger' },
						],
					}),
					form: {
						show: false,
					},
				},
				target_type: {
					title: t('message.pages.messageCenter.table.columns.targetType'),
					type: ['dict-radio', 'colspan'],
					column: {
						minWidth: 120,
					},
					dict: dict({
						data: [
							{ value: 0, label: t('message.pages.messageCenter.targetType.byUser') },
							{ value: 1, label: t('message.pages.messageCenter.targetType.byRole') },
							{ value: 2, label: t('message.pages.messageCenter.targetType.byDept') },
							{ value: 3, label: t('message.pages.messageCenter.targetType.notice') },
						],
					}),
					form: {
						component: {
							optionName: 'el-radio-button',
						},
						rules: [{ required: true, message: t('message.pages.messageCenter.validation.targetTypeRequired'), trigger: ['blur', 'change'] }],
					},
				},
				target_user: {
					title: t('message.pages.messageCenter.table.columns.targetUser'),
					search: {
						disabled: true,
					},
					form: {
						component: {
							name: shallowRef(tableSelector),
							vModel: 'modelValue',
							displayLabel: compute(({ row }) => {
								if (row) {
									return row.user_info;
								}
								return null;
							}),
							tableConfig: {
								url: '/api/system/user/',
								label: 'name',
								value: 'id',
								isMultiple: true,
								columns: [
									{
										prop: 'name',
										label: t('message.pages.user.table.columns.name'),
										width: 120,
									},
									{
										prop: 'phone',
										label: t('message.pages.messageCenter.form.phone'),
										width: 120,
									},
								],
							},
						},
						show: compute(({ form }) => {
							return form.target_type === 0;
						}),
						rules: [
							// 表单校验规则
							{ required: true, message: t('message.pages.messageCenter.validation.required') },
						],
					},
					column: {
						show: false,
						component: {
							name: shallowRef(manyToMany),
							vModel: 'modelValue',
							bindValue: compute(({ row }) => {
								return row.user_info;
							}),
							displayLabel: 'name',
						},
					},
				},
				target_role: {
					title: t('message.pages.messageCenter.table.columns.targetRole'),
					search: {
						disabled: true,
					},
					width: 130,
					form: {
						component: {
							name: shallowRef(tableSelector),
							vModel: 'modelValue',
							displayLabel: compute(({ row }) => {
								if (row) {
									return row.role_info;
								}
								return null;
							}),
							tableConfig: {
								url: '/api/system/role/',
								label: 'name',
								value: 'id',
								isMultiple: true,
								columns: [
									{
										prop: 'name',
										label: t('message.pages.messageCenter.form.roleName'),
									},
									{
										prop: 'key',
										label: t('message.pages.messageCenter.form.roleKey'),
									},
								],
							},
						},
						show: compute(({ form }) => {
							return form.target_type === 1;
						}),
						rules: [
							// 表单校验规则
							{
								required: true,
								message: t('message.pages.messageCenter.validation.required'),
							},
						],
					},
					column: {
						show: false,
						component: {
							name: shallowRef(manyToMany),
							vModel: 'modelValue',
							bindValue: compute(({ row }) => {
								return row.role_info;
							}),
							displayLabel: 'name',
						},
					},
				},
				target_dept: {
					title: t('message.pages.messageCenter.table.columns.targetDept'),
					search: {
						disabled: true,
					},
					width: 130,
					type: 'table-selector',
					form: {
						component: {
							name: shallowRef(tableSelector),
							vModel: 'modelValue',
							displayLabel: compute(({ form }) => {
								return form.dept_info;
							}),
							tableConfig: {
								url: '/api/system/dept/all_dept/',
								label: 'name',
								value: 'id',
								isTree: true,
								isMultiple: true,
								columns: [
									{
										prop: 'name',
										label: t('message.pages.messageCenter.form.deptName'),
										width: 150,
									},
									{
										prop: 'status_label',
										label: t('message.pages.messageCenter.form.status'),
									},
									{
										prop: 'parent_name',
										label: t('message.pages.messageCenter.form.parentDept'),
									},
								],
							},
						},
						show: compute(({ form }) => {
							return form.target_type === 2;
						}),
						rules: [
							// 表单校验规则
							{
								required: true,
								message: t('message.pages.messageCenter.validation.required'),
							},
						],
					},
					column: {
						show: false,
						component: {
							name: shallowRef(manyToMany),
							vModel: 'modelValue',
							bindValue: compute(({ row }) => {
								return row.dept_info;
							}),
							displayLabel: 'name',
						},
					},
				},
				content: {
					title: t('message.pages.messageCenter.table.columns.content'),
					column: {
						width: 300,
						show: false,
					},
					type: ['editor-wang5', 'colspan'],
					form: {
						rules: [
							// 表单校验规则
							{
								required: true,
								message: t('message.pages.messageCenter.validation.required'),
							},
						],
						component: {
							disabled: false,
							id: '1', // 当同一个页面有多个editor时，需要配置不同的id
							editorConfig: {
								// 是否只读
								readOnly: compute((context) => {
									const { mode } = context;
									if (mode === 'add') {
										return false;
									}
									return true;
								}),
							},
							uploader: {
								type: 'form',
								buildUrl(res: any) {
									return res.url;
								},
							},
						},
					},
				},
			},
		},
	};
}
