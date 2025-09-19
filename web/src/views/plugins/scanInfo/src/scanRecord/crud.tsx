import * as api from './api';
import { UserPageQuery, AddReq, DelReq, EditReq, CreateCrudOptionsProps, CreateCrudOptionsRet, dict } from '@fast-crud/fast-crud';
import {commonCrudConfig} from "/@/utils/commonCrud";
import {dictionary} from "/@/utils/dictionary";

export const createCrudOptions = function ({ crudExpose }: CreateCrudOptionsProps): CreateCrudOptionsRet {
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
			actionbar: {
				buttons: {
					add: {
						show: false,
					},
				},
			},
			rowHandle: {
				fixed:'right',
				width: 100,
				buttons: {
					view: {
						type: 'text',
					},
					edit: {
						show: false,
					},
					remove: {
						show: false,
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
							return ((pagination!.currentPage ?? 1) - 1) * pagination!.pageSize + index + 1;
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
				code: {
					title: '扫码数据',
					search: {
						show: true,
					},
					type: 'input',
					column:{
						width: 200,
					},
					form: {
						disabled: true,
						component: {
							placeholder: '请输入产品件号',
						},
					},
				},
				product_code: {
					title: '产品件号',
					search: {
						show: true,
					},
					type: 'input',
					column:{
						minWidth: 120,
					},
					form: {
						disabled: true,
						component: {
							placeholder: '请输入产品件号',
						},
					},
				},
				supplier_code: {
					title: '供应商代码',
					search: {
						show: true,
					},
					type: 'input',
					column:{
						minWidth: 120,
					},
					form: {
						disabled: true,
						component: {
							placeholder: '请输入供应商代码',
						},
					},
				},
				production_batch: {
					title: '生产批次',
					search: {
						show: true,
					},
					type: 'input',
					column:{
						minWidth: 120,
					},
					form: {
						disabled: true,
						component: {
							placeholder: '请输入生产批次',
						},
					},
				},
				product_serial_number: {
					title: '产品序列码',
					search: {
						show: true,
					},
					type: 'input',
					column:{
						minWidth: 120,
					},
					form: {
						disabled: true,
						component: {
							placeholder: '请输入产品序列码',
						},
					},
				},

				version_number: {
					title: '版本号',
					search: {
						show: true,
					},
					disabled: true,
					type: 'input',
					column:{
						minWidth: 120,
					},
					form: {
						component: {
							placeholder: '请输入版本号',
						},
					},
				},
				shift: {
					title: '班次',
					type: 'input',
					column:{
						minWidth: 90,
					},
					search: {
						show: true,
					},
					form: {
						disabled: true,
						component: {
							placeholder: '请输入班次',
						},
					},
					component: { props: { color: 'auto' } }, // 自动染色
				},
				status: {
                    title: '状态',
                    type: 'dict-select',
                    dict: dict({
                        data: [
                            { label: '重复扫码', value: 0 },
                            { label: '正常', value: 1 },
                            { label: '未识别码', value: 2 },
                        ]
                    }),
                    column: {
                        width: 120
                    },
                    search: {
                        show: true
                    }
                },
				...commonCrudConfig({
					create_datetime: { form: false, table: true, search: false, width: 160 },
					update_datetime: { form: false, table: true, search: false, width: 160 },
					creator_name: { form: false, table: true, search: false, width: 100 },
				})
			},
		},
	};
};
