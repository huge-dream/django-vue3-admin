import { useI18n } from 'vue-i18n';
import { CreateCrudOptionsProps, CreateCrudOptionsRet, AddReq, DelReq, EditReq, dict, compute } from '@fast-crud/fast-crud';
import * as api from './api';
import { dictionary } from '/@/utils/dictionary';
import { successMessage } from '../../../utils/message';
import { auth } from '/@/utils/authFunction';
import { nextTick, computed } from 'vue';

/**
 *
 * @param crudExpose：index传递过来的示例
 * @param context：index传递过来的自定义参数
 * @returns
 */
export const createCrudOptions = function ({ crudExpose, context }: CreateCrudOptionsProps): CreateCrudOptionsRet {
	const { t } = useI18n()
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

	return {
		crudOptions: {
			request: {
				pageRequest,
				addRequest,
				editRequest,
				delRequest,
			},
			pagination: {
				show: true,
			},
			actionbar: {
				buttons: {
					add: {
						show: auth('role:Create'),
					},
				},
			},
			rowHandle: {
				//固定右侧
				fixed: 'right',
				width:  computed(() => {
					if (auth('role:AllAuthorizedUser') || auth('role:AllCanMenu')){
						return 420;
					}
					return 320;
				}),
				buttons: {
					view: {
						iconRight: 'View',
						type: 'text',
						show: true,
					},
					edit: {
						iconRight: 'Edit',
						type: 'text',
						show: auth('role:Update'),
					},
					remove: {
						iconRight: 'Delete',
						type: 'text',
						show: auth('role:Delete'),
					},
					assignment: {
						iconRight: 'setting',
						type: 'text',
						text: t('message.pages.role.buttons.assignUsers'),
						show: auth('role:AllAuthorizedUser'),
						click: (ctx: any) => {
							const { row } = ctx;
							context!.RoleUserDrawer.handleDrawerOpen(row);
							nextTick(() => {
								context!.RoleUserRef.value.setSearchFormData({ form: { role_id: row.id } });
								context!.RoleUserRef.value.doRefresh();
							});
						},
					},
					permission: {
						iconRight:'setting',
						type: 'text',
						text: t('message.pages.role.buttons.assignPermission'),
						show: auth('role:SetMenu'),
						click: (clickContext: any): void => {
							const { row } = clickContext;
							context.RoleDrawer.handleDrawerOpen(row);
							context.RoleMenuBtn.setState([]);
							context.RoleMenuField.setState([]);
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
					title: t('message.pages.role.table.columns.index'),
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
					column: { show: false },
					search: { show: false },
					form: { show: false },
				},
				name: {
					title: t('message.pages.role.table.columns.name'),
					search: { show: true },
					column: {
						minWidth: 120,
						sortable: 'custom',
					},
					form: {
						rules: [{ required: true, message: t('message.pages.role.validation.nameRequired') }],
						component: {
							placeholder: t('message.pages.role.form.namePlaceholder'),
						},
					},
				},
				key: {
					title: t('message.pages.role.table.columns.key'),
					search: { show: false },
					column: {
						minWidth: 120,
						sortable: 'custom',
						columnSetDisabled: true,
					},
					form: {
						rules: [{ required: true, message: t('message.pages.role.validation.keyRequired') }],
						component: {
							placeholder: t('message.pages.role.form.keyPlaceholder'),
						},
					},
					valueBuilder(context) {
						const { row, key } = context;
						return row[key];
					},
				},
				sort: {
					title: t('message.pages.role.table.columns.sort'),
					search: { show: false },
					type: 'number',
					column: {
						minWidth: 90,
						sortable: 'custom',
					},
					form: {
						rules: [{ required: true, message: t('message.pages.role.validation.sortRequired') }],
						value: 1,
					},
				},
				status: {
					title: t('message.pages.role.table.columns.status'),
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
					},
					dict: dict({
						data: dictionary('button_status_bool'),
					}),
				},
			},
		},
	};
};
