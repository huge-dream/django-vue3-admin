import { CrudOptions, AddReq, DelReq, EditReq, dict, CrudExpose, compute } from '@fast-crud/fast-crud';
import * as api from './api';
import { dictionary } from '/@/utils/dictionary';
import { columnPermission } from '../../../utils/columnPermission';
import { successMessage } from '../../../utils/message';
import {auth} from '/@/utils/authFunction'
interface CreateCrudOptionsTypes {
	output: any;
	crudOptions: CrudOptions;
}

//此处为crudOptions配置
export const createCrudOptions = function ({
	crudExpose,
	rolePermission,
	handleDrawerOpen,
}: {
	crudExpose: CrudExpose;
	rolePermission: any;
	handleDrawerOpen: Function;
}): CreateCrudOptionsTypes {
	const pageRequest = async (query: any) => {
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

	//权限判定

	// @ts-ignore
	// @ts-ignore
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
						show: auth('role:Create')
					}
				}
			},
			rowHandle: {
				//固定右侧
				fixed: 'right',
				width: 320,
				buttons: {
					view: {
						show: true,
					},
					edit: {
						show: auth('role:Update'),
					},
					remove: {
						show: auth('role:Delete'),
					},
					permission: {
						type: 'primary',
						text: '权限配置',
						show: auth('role:Permission'),
						tooltip: {
							placement: 'top',
							content: '权限配置',
						},
						click: (context: any): void => {
							const { row } = context;
							handleDrawerOpen(row);
						},
					},
				},
			},
			form: {
				col: { span: 24 },
				labelWidth: '100px',
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
						type: 'index',
						align: 'center',
						width: '70px',
						columnSetDisabled: true, //禁止在列设置中选择
					},
				},
				id: {
					title: 'ID',
					type: 'text',
					column: { show: false },
					search: { show: false },
					form: { show: false },
				},
				name: {
					title: '角色名称',
					type: 'text',
					search: { show: true },
					column: {
						minWidth: 120,
						sortable: 'custom',
						show: columnPermission('name', 'is_query'),
					},
					// addForm: {
					// 	show: columnPermission('name', 'is_create'),
					// },
					editForm: {
						show: columnPermission('name', 'is_update'),
					},
					form: {
						rules: [{ required: true, message: '角色名称必填' }],
						component: {
							placeholder: '请输入角色名称',
						},
					},
				},
				key: {
					title: '权限标识',
					type: 'text',
					search: { show: false },
					column: {
						minWidth: 120,
						sortable: 'custom',
						show: columnPermission('key', 'is_query'),
						columnSetDisabled: true,
					},
					addForm: {
						show: columnPermission('key', 'is_create'),
					},
					editForm: {
						show: columnPermission('key', 'is_update'),
					},
					form: {
						rules: [{ required: true, message: '权限标识必填' }],
						component: {
							placeholder: '输入权限标识',
						},
					},
					valueBuilder(context){
						const {row,key} = context
						return row[key]
					}
				},
				sort: {
					title: '排序',
					search: { show: false },
					type: 'number',
					column: {
						minWidth: 90,
						sortable: 'custom',
					},
					addForm: {
						show: columnPermission('sort', 'is_create'),
					},
					editForm: {
						show: columnPermission('sort', 'is_update'),
					},
					form: {
						rules: [{ required: true, message: '排序必填' }],
						value: 1,
					},
				},
				status: {
					title: '状态',
					search: { show: true },
					type: 'dict-radio',
					column: {
						width: 100,
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
						show: columnPermission('status', 'is_query'),
					},
					addForm: {
						show: columnPermission('status', 'is_create'),
					},
					editForm: {
						show: columnPermission('status', 'is_update'),
					},
					dict: dict({
						data: dictionary('button_status_bool'),
					}),
				},
				update_datetime: {
					title: '更新时间',
					type: 'text',
					search: { show: false },
					column: {
						minWidth: 170,
						sortable: 'custom',
						show: columnPermission('update_datetime', 'is_query'),
					},
					form: {
						show: false,
						component: {
							placeholder: '输入关键词搜索',
						},
					},
				},
				create_datetime: {
					title: '创建时间',
					type: 'text',
					search: { show: false },
					column: {
						sortable: 'custom',
						minWidth: 170,
						show: columnPermission('create_datetime', 'is_query'),
					},
					form: {
						show: false,
						component: {
							placeholder: '输入关键词搜索',
						},
					},
				},
				// description: {
				//     title: '备注',
				//     type: 'textarea',
				//     search: {show: false},
				//     form: {
				//         component: {
				//             maxlength: 200,
				//             placeholder: '输入备注',
				//         },
				//     },
				// },
			},
		},
	};
};
