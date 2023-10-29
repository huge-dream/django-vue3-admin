import * as api from './api';
import { dict, UserPageQuery, AddReq, DelReq, EditReq, compute, CreateCrudOptionsProps, CreateCrudOptionsRet } from '@fast-crud/fast-crud';
import { request } from '/@/utils/service';
import { dictionary } from '/@/utils/dictionary';
import { successMessage, successNotification, warningNotification } from '/@/utils/message';
import { inject } from 'vue';
import { automatchColumnsData } from '/@/views/system/columns/components/ColumnsTableCom/api';

export const createCrudOptions = function ({ crudExpose, props }: CreateCrudOptionsProps): CreateCrudOptionsRet {
	const pageRequest = async (query: UserPageQuery) => {
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
		form.role = props.role;
		form.model = props.model;
		form.model = props.app;
		return await api.AddObj(form);
	};

	/**
	 * 自动匹配列
	 */
	const handleAutomatch = async () => {
		if (props.role && props.model && props.app) {
			const res = await automatchColumnsData(props);
			if (res?.code === 2000) {
				successNotification('匹配成功');
			}
			crudExpose.doSearch({ form: { role: props.role, model: props.model, app: props.app } });
		}
		warningNotification('请选择角色和模型表！');
	};

	//权限判定
	const hasPermissions = inject('$hasPermissions');

	return {
		crudOptions: {
			request: {
				pageRequest,
				addRequest,
				editRequest,
				delRequest,
			},
			pagination: {
				show: false,
			},
			actionbar: {
				buttons: {
					auto: {
						text: '自动匹配',
						type: 'success',
						click: () => {
							return handleAutomatch();
						},
					},
				},
			},
			rowHandle: {
				//固定右侧
				fixed: 'right',
			},
			form: {
				col: { span: 24 },
				labelWidth: '110px',
				wrapper: {
					is: 'el-dialog',
					width: '600px',
				},
			},
			columns: {
				_index: {
					title: '序号',
					form: { show: false },
					column: {
						//type: 'index',
						align: 'center',
						width: '70px',
						columnSetDisabled: true, //禁止在列设置中选择
						//@ts-ignore
						formatter: (context) => {
							//计算序号,你可以自定义计算规则，此处为翻页累加
							let index = context.index ?? 1;
							let pagination: any = crudExpose!.crudBinding.value.pagination;
							return ((pagination.currentPage ?? 1) - 1) * pagination.pageSize + index + 1;
						},
					},
				},
				field_name: {
					title: '字段名',
					type: 'text',
					search: {
						show: true,
					},
					column: {
						width: 150,
					},
				},
				title: {
					title: '中文名',
					sortable: 'custom',
					search: {
						show: true,
					},
					type: 'text',
					column: {
						width: 100,
					},
					form: {
						rules: [
							// 表单校验规则
							{
								required: true,
								message: '必填项',
							},
						],
						component: {
							span: 12,
						},
					},
				},
				is_create: {
					title: '创建时显示',
					sortable: 'custom',
					search: {
						disabled: true,
					},
					type: 'dict-switch',
					dict: dict({
						data: [
							{ value: true, label: '启用' },
							{ value: false, label: '禁用' },
						],
					}),
					form: {
						value: true,
					},
					column: {
						valueChange(context){
							return api.UpdateObj(context.row)
						},
						component: {
							name: 'fs-dict-switch',
						},
					},
				},
				is_update: {
					title: '编辑时显示',
					search: {
						show: true,
					},
					type: 'dict-switch',
					dict: dict({
						data: [
							{ value: true, label: '启用' },
							{ value: false, label: '禁用' },
						],
					}),
					form: {
						value: true,
					},
					column: {
						component: {
							name: 'fs-dict-switch',
							onChange: compute((context) => {
								//动态onChange方法测试
								return () => {
									console.log('onChange', context.row.switch);
								};
							}),
						},
					},
				},
				is_query: {
					title: '列表中显示',
					type: 'dict-switch',
					dict: dict({
						data: [
							{ value: true, label: '启用' },
							{ value: false, label: '禁用' },
						],
					}),
					form: {
						value: true,
					},
					column: {
						component: {
							name: 'fs-dict-switch',
							onChange: compute((context) => {
								//动态onChange方法测试
								return () => {
									console.log('onChange', context.row.switch);
								};
							}),
						},
					},
				},
			},
		},
	};
};
