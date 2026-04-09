import { inject } from 'vue';
import { useI18n } from 'vue-i18n';
import { dict, UserPageQuery, AddReq, DelReq, EditReq, compute, CreateCrudOptionsProps, CreateCrudOptionsRet } from '@fast-crud/fast-crud';
import { request } from '/@/utils/service';
import * as api from './api';
import { dictionary } from '/@/utils/dictionary';
import { successMessage } from '/@/utils/message';
import { auth } from "/@/utils/authFunction";

export const createCrudOptions = function ({ crudExpose, context }: CreateCrudOptionsProps): CreateCrudOptionsRet {
	const { t } = useI18n()
	const pageRequest = async (query: UserPageQuery) => {
		const show_all = context?.isShowChildFlag.value ? '1' : '0';
		const res = await api.GetList({ ...query, show_all });
		/**
		 * 处理crud警告：Invalid prop: type check failed for prop "name". Expected String with value "2", got Number with value 2.
		 */
		// res.data.forEach((item: any) => {
		// 	item.dept = String(item.dept);
		// 	if (item.role && Array.isArray(item.role) && item.role.length > 0) {
		// 		item.role = item.role.map((r: number) => String(r));
		// 	}
		// });
		return res;
	};
	const editRequest = async ({ form, row }: EditReq) => {
		form.id = row.id;
		return await api.UpdateObj(form);
	};
	const delRequest = async ({ row }: DelReq) => {
		const res = await api.DelObj(row.id);
		context?.getDeptInfo();
		return res;
	};
	const addRequest = async ({ form }: AddReq) => {
		const res = await api.AddObj(form);
		context?.getDeptInfo();
		return res;
	};

	const exportRequest = async (query: UserPageQuery) => {
		return await api.exportData(query);
	};

	return {
		crudOptions: {
			table: {
				remove: {
					confirmMessage: t('message.pages.dept.user.deleteUserConfirm'),
				},
			},
			request: {
				pageRequest,
				addRequest,
				editRequest,
				delRequest,
			},
			actionbar: {
				buttons: {
					add: {
						show: auth('user:Create')
					},
					export: {
						text: t('message.pages.dept.user.tableColumns.export'),
						title: t('message.pages.dept.user.tableColumns.export'),
						show: auth('user:Export'),
						click() {
							return exportRequest(crudExpose!.getSearchFormData());
						},
					},
				},
			},
			search: {
				container: {
					layout: 'multi-line',
					action: {
						col: {
							span: 10,
						},
					},
				},
			},
			rowHandle: {
				//固定右侧
				fixed: 'right',
				width: 260,
				buttons: {
					view: {
						show: false,
					},
					edit: {
						iconRight: 'edit',
                        type: 'text',
						show: auth('user:Update'),
					},
					remove: {
						iconRight: 'Delete',
                        type: 'text',
						show: auth('user:Delete'),
					},
					custom: {
						iconRight:'Setting',
						text: t('message.pages.dept.user.tableColumns.resetPassword'),
						type: 'text',
						show: auth('user:ResetPassword'),
						tooltip: {
							placement: 'top',
							content: t('message.pages.dept.user.tableColumns.resetPasswordTooltip'),
						},
						click: (ctx: any) => context?.handleResetPwdOpen(ctx.row),
					},
				},
			},
			columns: {
				_index: {
					title: t('message.pages.dept.user.tableColumns.index'),
					form: { show: false },
					column: {
						type: 'index',
						align: 'center',
						width: '70px',
						columnSetDisabled: true, //禁止在列设置中选择
					},
				},
				search: {
					title: t('message.pages.dept.user.tableColumns.keyword'),
					column: {
						show: false,
					},
					search: {
						show: true,
						component: {
							props: {
								clearable: true,
							},
							placeholder: t('message.pages.dept.user.tableColumns.keywordPlaceholder'),
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
				username: {
					title: t('message.pages.dept.user.tableColumns.username'),
					type: 'input',
					column: {
						minWidth: 100, //最小列宽
					},
					form: {
						rules: [
							// 表单校验规则
							{
								required: true,
								message: t('message.pages.dept.user.tableColumns.usernameRequired'),
							},
						],
						component: {
							placeholder: t('message.pages.dept.user.tableColumns.usernamePlaceholder'),
						},
					},
				},
				password: {
					title: t('message.pages.dept.user.tableColumns.password'),
					type: 'input',
					column: {
						show: false,
					},
					editForm: {
						show: false,
					},
					form: {
						rules: [
							// 表单校验规则
							{
								required: true,
								message: t('message.pages.dept.user.tableColumns.passwordRequired'),
							},
						],
						component: {
							span: 12,
							showPassword: true,
							placeholder: t('message.pages.dept.user.tableColumns.passwordPlaceholder'),
						},
						// value: vm.systemConfig('base.default_password'),
					},
					/* valueResolve(row, key) {
						if (row.password) {
							row.password = vm.$md5(row.password)
						}
					} */
				},
				name: {
					title: t('message.pages.dept.user.tableColumns.name'),
					type: 'input',
					column: {
						minWidth: 100, //最小列宽
					},
					form: {
						rules: [
							// 表单校验规则
							{
								required: true,
								message: t('message.pages.dept.user.tableColumns.nameRequired'),
							},
						],
						component: {
							span: 12,
							placeholder: t('message.pages.dept.user.tableColumns.namePlaceholder'),
						},
					},
				},
				dept: {
					title: t('message.pages.dept.user.tableColumns.dept'),
					type: 'dict-tree',
					dict: dict({
						isTree: true,
						url: '/api/system/dept/all_dept/',
						value: 'id',
						label: 'name',
					}),
					column: {
						minWidth: 200, //最小列宽
						formatter({ value, row, index }) {
							return row.dept_name_all
						}
					},
					form: {
						rules: [
							// 表单校验规则
							{
								required: true,
								message: t('message.pages.dept.user.tableColumns.deptRequired'),
							},
						],
						component: {
							filterable: true,
							placeholder: t('message.pages.dept.user.tableColumns.selectDeptPlaceholder'),
							props: {
								props: {
									value: 'id',
									label: 'name',
								},
							},
						},
					},
				},
				role: {
					title: t('message.pages.dept.user.tableColumns.role'),
					search: {
						show: true,
						component: {
							props: {
								clearable: true,
							},
						},
					},
					type: 'dict-select',
					dict: dict({
						url: '/api/system/role/',
						value: 'id',
						label: 'name',
					}),
					column: {
						minWidth: 200, //最小列宽
						// formatter({ value, row, index }) {
						// 	const values = row.role_info.map((item: any) => item.name);
						// 	return values.join(',')
						// }
					},
					form: {
						rules: [
							// 表单校验规则
							{
								required: true,
								message: t('message.pages.dept.user.tableColumns.deptRequired'),
							},
						],
						component: {
							multiple: true,
							filterable: true,
							placeholder: t('message.pages.dept.user.tableColumns.rolePlaceholder'),
						},
					},
				},
				mobile: {
					title: t('message.pages.dept.user.tableColumns.mobile'),
					type: 'input',
					column: {
						minWidth: 120, //最小列宽
					},
					form: {
						rules: [
							{
								max: 20,
								message: t('message.pages.dept.user.tableColumns.mobileInvalid'),
								trigger: 'blur',
							},
							{
								pattern: /^1[3-9]\d{9}$/,
								message: t('message.pages.dept.user.tableColumns.mobileInvalid'),
							},
						],
						component: {
							placeholder: t('message.pages.dept.user.tableColumns.mobilePlaceholder'),
						},
					},
				},
				email: {
					title: t('message.pages.dept.user.tableColumns.email'),
					column: {
						width: 260,
					},
					form: {
						rules: [
							{
								type: 'email',
								message: t('message.pages.dept.user.tableColumns.emailInvalid'),
								trigger: ['blur', 'change'],
							},
						],
						component: {
							placeholder: t('message.pages.dept.user.tableColumns.emailPlaceholder'),
						},
					},
				},
				gender: {
					title: t('message.pages.dept.user.tableColumns.gender'),
					type: 'dict-select',
					dict: dict({
						data: dictionary('gender'),
					}),
					form: {
						value: 1,
						component: {
							span: 12,
						},
					},
					component: { props: { color: 'auto' } }, // 自动染色
				},
				user_type: {
					title: t('message.pages.dept.user.tableColumns.userType'),
					search: {
						show: true,
					},
					type: 'dict-select',
					dict: dict({
						data: dictionary('user_type'),
					}),
					column: {
						minWidth: 100, //最小列宽
					},
					form: {
						show: false,
						value: 0,
						component: {
							span: 12,
						},
					},
				},
				is_active: {
					title: t('message.pages.dept.user.tableColumns.locked'),
					search: {
						show: true,
					},
					type: 'dict-radio',
					column: {
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
				avatar: {
					title: t('message.pages.dept.user.tableColumns.avatar'),
					type: 'avatar-uploader',
					form: {
						show: false,
					},
					column: {
						width: 100,
						showOverflowTooltip: true,
					}
				},
			},
		},
	};
};
