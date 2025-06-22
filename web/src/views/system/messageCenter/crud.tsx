import * as api from './api';
import { dict, useCompute, PageQuery, AddReq, DelReq, EditReq, CreateCrudOptionsProps, CreateCrudOptionsRet } from '@fast-crud/fast-crud';
import tableSelector from '/@/components/tableSelector/index.vue';
import { shallowRef, computed } from 'vue';
import manyToMany from '/@/components/manyToMany/index.vue';
import { auth } from '/@/utils/authFunction';
const { compute } = useCompute();

export default function ({ crudExpose, context }: CreateCrudOptionsProps): CreateCrudOptionsRet {
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
				width: 150,
				buttons: {
					edit: {
						show: false,
					},
					view: {
						text: '查看',
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
					title: '标题',
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
								message: '必填项',
							},
						],
						component: { span: 24, placeholder: '请输入标题' },
					},
				},
				is_read: {
					title: '是否已读',
					type: 'dict-select',
					column: {
						show: IsReadFunc.value,
					},
					dict: dict({
						data: [
							{ label: '已读', value: true, color: 'success' },
							{ label: '未读', value: false, color: 'danger' },
						],
					}),
					form: {
						show: false,
					},
				},
				target_type: {
					title: '目标类型',
					type: ['dict-radio', 'colspan'],
					column: {
						minWidth: 120,
					},
					dict: dict({
						data: [
							{ value: 0, label: '按用户' },
							{ value: 1, label: '按角色' },
							{ value: 2, label: '按部门' },
							{ value: 3, label: '通知公告' },
						],
					}),
					form: {
						component: {
							optionName: 'el-radio-button',
						},
						rules: [{ required: true, message: '必选项', trigger: ['blur', 'change'] }],
					},
				},
				target_user: {
					title: '目标用户',
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
										label: '用户名称',
										width: 120,
									},
									{
										prop: 'phone',
										label: '用户电话',
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
							{ required: true, message: '必填项' },
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
					title: '目标角色',
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
										label: '角色名称',
									},
									{
										prop: 'key',
										label: '权限标识',
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
								message: '必填项',
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
					title: '目标部门',
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
										label: '部门名称',
										width: 150,
									},
									{
										prop: 'status_label',
										label: '状态',
									},
									{
										prop: 'parent_name',
										label: '父级部门',
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
								message: '必填项',
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
					title: '内容',
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
								message: '必填项',
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
