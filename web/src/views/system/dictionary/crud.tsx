import * as api from './api';
import { dict, UserPageQuery, AddReq, DelReq, EditReq, compute, CreateCrudOptionsProps, CreateCrudOptionsRet } from '@fast-crud/fast-crud';
import { dictionary } from '/@/utils/dictionary';
import { inject, nextTick, ref } from 'vue';
import { successMessage } from '/@/utils/message';
import {auth} from '/@/utils/authFunction';
export const createCrudOptions = function ({ crudExpose, context }: CreateCrudOptionsProps): CreateCrudOptionsRet {
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
			rowHandle: {
				fixed: 'right',
				width: 200,
				buttons: {
					view: {
						show: false,
					},
					edit: {
						iconRight: 'Edit',
						type: 'text',
						show: auth('dictionary:Update'),
					},
					remove: {
						iconRight: 'Delete',
						type: 'text',
						show: auth('dictionary:Delete'),
					},
					custom: {
						text: '字典配置',
						type: 'text',
						show: auth('dictionary:Update'),
						tooltip: {
							placement: 'top',
							content: '字典配置',
						},
						//@ts-ignore
						click: (ctx: any) => {
							const { row } = ctx;
							context!.subDictRef.value.drawer = true;
							nextTick(() => {
								context!.subDictRef.value.setSearchFormData({ form: { parent: row.id } });
								context!.subDictRef.value.doRefresh();
							});
						},
					},
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
						formatter: (context) => {
							//计算序号,你可以自定义计算规则，此处为翻页累加
							let index = context.index ?? 1;
							let pagination = crudExpose!.crudBinding.value.pagination;
							// @ts-ignore
							return ((pagination.currentPage ?? 1) - 1) * pagination.pageSize + index + 1;
						},
					},
				},
				search: {
					title: '关键词',
					column: {
						show: false,
					},
					search: {
						show: true,
						component: {
							props: {
								clearable: true,
							},
							placeholder: '请输入关键词',
						},
					},
					form: {
						show: false,
						component: {
							props: {
								clearable: true,
							},
						},
					},
				},
				label: {
					title: '字典名称',
					search: {
						show: true,
						component: {
							props: {
								clearable: true,
							},
						},
					},
					type: 'input',
					column: {
						minWidth: 120,
					},
					form: {
						rules: [
							// 表单校验规则
							{ required: true, message: '字典名称必填项' },
						],
						component: {
							props: {
								clearable: true,
							},
							placeholder: '请输入字典名称',
						},
					},
				},
				value: {
					title: '字典编号',
					search: {
						disabled: true,
						component: {
							props: {
								clearable: true,
							},
						},
					},
					type: 'input',
					column: {
						minWidth: 120,
					},
					form: {
						rules: [
							// 表单校验规则
							{ required: true, message: '字典编号必填项' },
						],
						component: {
							props: {
								clearable: true,
							},
							placeholder: '请输入字典编号',
						},
						helper: {
							render(h) {
								return <el-alert title="使用方法：dictionary('字典编号')" type="warning" />;
							},
						},
					},
				},
				status: {
					title: '状态',
					search: {
						show: true,
					},
					type: 'dict-radio',
					column: {
						minWidth: 90,
						component: {
							name: 'fs-dict-switch',
							activeText: '',
							inactiveText: '',
							style: '--el-switch-on-color: var(--el-color-primary); --el-switch-off-color: #dcdfe6',
							onChange: compute((context) => {
								return () => {
									api.UpdateObj(context.row).then((res: APIResponseData) => {
										successMessage(res.msg as string);
									});
								};
							}),
						},
					},
					dict: dict({
						data: dictionary('button_status_bool'),
					}),
				},
				sort: {
					title: '排序',
					type: 'number',
					column: {
						minWidth: 80,
					},
					form: {
						value: 1,
					},
				},
			},
		},
	};
};
