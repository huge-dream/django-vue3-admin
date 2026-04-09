import * as api from './api';
import { UserPageQuery, AddReq, DelReq, EditReq, CrudExpose, CrudOptions, CreateCrudOptionsProps, CreateCrudOptionsRet } from '@fast-crud/fast-crud';
import { useI18n } from 'vue-i18n';

export const createCrudOptions = function ({ crudExpose }: CreateCrudOptionsProps): CreateCrudOptionsRet {
	const { t } = useI18n()
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
					title: t('message.pages.operationLog.table.columns.index'),
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
					title: t('message.pages.operationLog.table.columns.keyword'),
					column: {
						show: false,
					},
					search: {
						show: true,
						component: {
							props: {
								clearable: true,
							},
							placeholder: t('message.pages.operationLog.form.keywordPlaceholder'),
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
				request_modular: {
					title: t('message.pages.operationLog.table.columns.requestModule'),
					search: {
						disabled: false,
					},
					type: 'input',
					column:{
						minWidth: 100,
					},
					form: {
						disabled: true,
						component: {
							placeholder: t('message.pages.operationLog.form.requestModulePlaceholder'),
						},
					},
				},
				request_path: {
					title: t('message.pages.operationLog.table.columns.requestPath'),
					search: {
						disabled: false,
					},
					type: 'input',
					column:{
						minWidth: 200,
					},
					form: {
						disabled: true,
						component: {
							placeholder: t('message.pages.operationLog.form.requestPathPlaceholder'),
						},
					},
				},
				request_body: {
					column: {
						showOverflowTooltip: true,
						width: 200, //列宽
						minWidth: 100, //最小列宽
					},
					title: t('message.pages.operationLog.table.columns.requestBody'),
					search: {
						disabled: true,
					},
					disabled: true,
					type: 'textarea',
					form: {
						component: {
							props: {
								type: 'textarea',
							},
							autosize: {
								minRows: 2,
								maxRows: 8,
							},
							placeholder: t('message.pages.operationLog.form.requestBodyPlaceholder'),
						},
					},
				},
				request_method: {
					title: t('message.pages.operationLog.table.columns.requestMethod'),
					type: 'input',
					search: {
						disabled: false,
					},
					column:{
						minWidth: 100,
					},
					form: {
						disabled: true,
						component: {
							placeholder: t('message.pages.operationLog.form.requestMethodPlaceholder'),
						},
					},
					component: { props: { color: 'auto' } }, // 自动染色
				},
				request_msg: {
					title: t('message.pages.operationLog.table.columns.requestMsg'),
					disabled: true,
					form: {
						component: {
							span: 12,
						},
					},
				},
				request_ip: {
					title: t('message.pages.operationLog.table.columns.requestIp'),
					search: {
						disabled: false,
					},
					type: 'input',
					column:{
						minWidth: 100,
					},
					form: {
						disabled: true,
						component: {
							placeholder: t('message.pages.operationLog.form.requestIpPlaceholder'),
						},
					},
					component: { props: { color: 'auto' } }, // 自动染色
				},
				request_browser: {
					title: t('message.pages.operationLog.table.columns.requestBrowser'),
					type: 'input',
					column:{
						minWidth: 120,
					},
					form: {
						disabled: true,
					},
					component: { props: { color: 'auto' } }, // 自动染色
				},
				response_code: {
					title: t('message.pages.operationLog.table.columns.responseCode'),
					search: {
						disabled: true,
					},
					type: 'input',
					column:{
						minWidth: 100,
					},
					form: {
						disabled: true,
					},
					component: { props: { color: 'auto' } }, // 自动染色
				},
				request_os: {
					title: t('message.pages.operationLog.table.columns.requestOs'),
					disabled: true,
					search: {
						disabled: true,
					},
					type: 'input',
					column:{
						minWidth: 120,
					},
					form: {
						disabled: true,
					},
					component: { props: { color: 'auto' } }, // 自动染色
				},
				json_result: {
					title: t('message.pages.operationLog.table.columns.jsonResult'),
					search: {
						disabled: true,
					},
					type: 'input',
					column:{
						minWidth: 150,
					},
					form: {
						disabled: true,
					},
					component: { props: { color: 'auto' } }, // 自动染色
				},
				creator_name: {
					title: t('message.pages.operationLog.table.columns.creatorName'),
					column:{
						minWidth: 100,
					},
					form: {
						disabled: true,
					},
				},
			},
		},
	};
};
