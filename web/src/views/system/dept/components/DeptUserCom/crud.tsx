import { inject } from 'vue';
import { dict, UserPageQuery, AddReq, DelReq, EditReq, compute, CreateCrudOptionsProps, CreateCrudOptionsRet } from '@fast-crud/fast-crud';
import { request } from '/@/utils/service';
import * as api from './api';
import { dictionary } from '/@/utils/dictionary';
import { successMessage } from '/@/utils/message';
import { auth } from "/@/utils/authFunction";

export const createCrudOptions = function ({ crudExpose, context }: CreateCrudOptionsProps): CreateCrudOptionsRet {
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
					confirmMessage: '是否删除该用户？',
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
						text: '导出', //按钮文字
						title: '导出', //鼠标停留显示的信息
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
				width: 250,
				buttons: {
					view: {
						show: false,
					},
					edit: {
						show: auth('user:Update'),
					},
					remove: {
						show: auth('user:Delete'),
					},
					custom: {
						text: '重设密码',
						type: 'primary',
						show: auth('user:ResetPassword'),
						tooltip: {
							placement: 'top',
							content: '重设密码',
						},
						click: (ctx: any) => context?.handleResetPwdOpen(ctx.row),
					},
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
				username: {
					title: '账号',
					type: 'input',
					column: {
						minWidth: 100, //最小列宽
					},
					form: {
						rules: [
							// 表单校验规则
							{
								required: true,
								message: '账号必填项',
							},
						],
						component: {
							placeholder: '请输入账号',
						},
					},
				},
				password: {
					title: '密码',
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
								message: '密码必填项',
							},
						],
						component: {
							span: 12,
							showPassword: true,
							placeholder: '请输入密码',
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
					title: '姓名',
					type: 'input',
					column: {
						minWidth: 100, //最小列宽
					},
					form: {
						rules: [
							// 表单校验规则
							{
								required: true,
								message: '姓名必填项',
							},
						],
						component: {
							span: 12,
							placeholder: '请输入姓名',
						},
					},
				},
				dept: {
					title: '部门',
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
								message: '必填项',
							},
						],
						component: {
							filterable: true,
							placeholder: '请选择',
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
					title: '角色',
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
								message: '必填项',
							},
						],
						component: {
							multiple: true,
							filterable: true,
							placeholder: '请选择角色',
						},
					},
				},
				mobile: {
					title: '手机号码',
					type: 'input',
					column: {
						minWidth: 120, //最小列宽
					},
					form: {
						rules: [
							{
								max: 20,
								message: '请输入正确的手机号码',
								trigger: 'blur',
							},
							{
								pattern: /^1[3-9]\d{9}$/,
								message: '请输入正确的手机号码',
							},
						],
						component: {
							placeholder: '请输入手机号码',
						},
					},
				},
				email: {
					title: '邮箱',
					column: {
						width: 260,
					},
					form: {
						rules: [
							{
								type: 'email',
								message: '请输入正确的邮箱地址',
								trigger: ['blur', 'change'],
							},
						],
						component: {
							placeholder: '请输入邮箱',
						},
					},
				},
				gender: {
					title: '性别',
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
					title: '用户类型',
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
					title: '锁定',
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
					title: '头像',
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
