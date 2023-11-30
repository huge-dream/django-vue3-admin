import * as api from './api';
import { dict, UserPageQuery, AddReq, DelReq, EditReq, compute, CreateCrudOptionsProps, CreateCrudOptionsRet } from '@fast-crud/fast-crud';
import { request } from '/@/utils/service';
import { dictionary } from '/@/utils/dictionary';
import { inject } from 'vue';
import {auth} from "/@/utils/authFunction";



export const createCrudOptions = function ({ crudExpose, props,modelDialog,selectOptions,allModelData }: CreateCrudOptionsProps): CreateCrudOptionsRet {
	const pageRequest = async (query: UserPageQuery) => {
		// return await api.GetList(query);
		if (selectOptions.value.id) {
			return await api.GetList({ menu: selectOptions.value.id } as any);
		} else {
			return undefined;
		}
	};
	const editRequest = async ({ form, row }: EditReq) => {
		form.id = row.id;
		return await api.UpdateObj(form);
	};
	const delRequest = async ({ row }: DelReq) => {
		return await api.DelObj(row.id);
	};
	const addRequest = async ({ form }: AddReq) => {
		form.menu = selectOptions.value.id;
		return await api.AddObj(form);
	};

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
					add:{
						show:auth('column:Create')
					},
					auto: {
						text: '自动匹配',
						type: 'success',
						show:auth('column:Match'),
						click: () => {
							return modelDialog.value=true;
						},
					},
				},
			},
			rowHandle: {
				//固定右侧
				fixed: 'right',
				buttons: {
					view: {
						show: false,
					},
					edit: {
						show: auth('column:Update')
					},
					remove: {
						show: auth('column:Delete')
					},
				},
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
				model: {
					title: 'model',
					type: 'dict-select',
					dict:dict({
						url:'/api/system/column/get_models/',
						label:'title',
						value:'key'
					}),
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
				title: {
					title: '中文名',
					sortable: 'custom',
					search: {
						show: true,
					},
					type: 'text',
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
							placeholder: '请输入中文名',
						},
					},
				},
				field_name: {
					title: '字段名',
					type: 'text',
					search: {
						show: true,
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
							placeholder: '请输入字段名',
						},
					},
				},

				// is_create: {
				// 	title: '创建时显示',
				// 	sortable: 'custom',
				// 	search: {
				// 		disabled: true,
				// 	},
				// 	type: 'dict-switch',
				// 	dict: dict({
				// 		data: [
				// 			{ value: true, label: '启用' },
				// 			{ value: false, label: '禁用' },
				// 		],
				// 	}),
				// 	form: {
				// 		value: true,
				// 	},
				// 	column: {
				// 		valueChange(context){
				// 			return api.UpdateObj(context.row)
				// 		},
				// 		component: {
				// 			name: 'fs-dict-switch',
				// 		},
				// 	},
				// },
				// is_update: {
				// 	title: '编辑时显示',
				// 	search: {
				// 		show: true,
				// 	},
				// 	type: 'dict-switch',
				// 	dict: dict({
				// 		data: [
				// 			{ value: true, label: '启用' },
				// 			{ value: false, label: '禁用' },
				// 		],
				// 	}),
				// 	form: {
				// 		value: true,
				// 	},
				// 	column: {
				// 		component: {
				// 			name: 'fs-dict-switch',
				// 			onChange: compute((context) => {
				// 				//动态onChange方法测试
				// 				return () => {
				// 					console.log('onChange', context.row.switch);
				// 				};
				// 			}),
				// 		},
				// 	},
				// },
				// is_query: {
				// 	title: '列表中显示',
				// 	type: 'dict-switch',
				// 	dict: dict({
				// 		data: [
				// 			{ value: true, label: '启用' },
				// 			{ value: false, label: '禁用' },
				// 		],
				// 	}),
				// 	form: {
				// 		value: true,
				// 	},
				// 	column: {
				// 		component: {
				// 			name: 'fs-dict-switch',
				// 			onChange: compute((context) => {
				// 				//动态onChange方法测试
				// 				return () => {
				// 					console.log('onChange', context.row.switch);
				// 				};
				// 			}),
				// 		},
				// 	},
				// },
			},
		},
	};
};
