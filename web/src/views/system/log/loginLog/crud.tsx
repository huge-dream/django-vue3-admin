import * as api from './api';
import { UserPageQuery, AddReq, DelReq, EditReq, CreateCrudOptionsProps, CreateCrudOptionsRet, dict } from '@fast-crud/fast-crud';
import { useI18n } from 'vue-i18n';
import {commonCrudConfig} from "/@/utils/commonCrud";

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
					title: t('message.pages.loginLog.table.columns.index'),
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
					title: t('message.pages.loginLog.table.columns.keyword'),
					column: {
						show: false,
					},
					search: {
						show: true,
						component: {
							props: {
								clearable: true,
							},
							placeholder: t('message.pages.loginLog.form.keywordPlaceholder'),
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
					title: t('message.pages.loginLog.table.columns.username'),
					search: {
						disabled: false,
					},
					type: 'input',
					column:{
						minWidth: 120,
					},
					form: {
						disabled: true,
						component: {
							placeholder: t('message.pages.loginLog.form.usernamePlaceholder'),
						},
					},
				},
				ip: {
					title: t('message.pages.loginLog.table.columns.ip'),
					search: {
						disabled: false,
					},
					type: 'input',
					column:{
						minWidth: 120,
					},
					form: {
						disabled: true,
						component: {
							placeholder: t('message.pages.loginLog.form.ipPlaceholder'),
						},
					},
				},
				isp: {
					title: t('message.pages.loginLog.table.columns.isp'),
					search: {
						disabled: true,
					},
					disabled: true,
					type: 'input',
					column:{
						minWidth: 120,
					},
					form: {
						component: {
							placeholder: t('message.pages.loginLog.form.ispPlaceholder'),
						},
					},
				},
				continent: {
					title: t('message.pages.loginLog.table.columns.continent'),
					type: 'input',
					column:{
						minWidth: 90,
					},
					form: {
						disabled: true,
						component: {
							placeholder: t('message.pages.loginLog.form.continentPlaceholder'),
						},
					},
					component: { props: { color: 'auto' } }, // 自动染色
				},
				country: {
					title: t('message.pages.loginLog.table.columns.country'),
					type: 'input',
					column:{
						minWidth: 90,
					},
					form: {
						component: {
							placeholder: t('message.pages.loginLog.form.countryPlaceholder'),
						},
					},
					component: { props: { color: 'auto' } }, // 自动染色
				},
				province: {
					title: t('message.pages.loginLog.table.columns.province'),
					type: 'input',
					column:{
						minWidth: 80,
					},
					form: {
						component: {
							placeholder: t('message.pages.loginLog.form.provincePlaceholder'),
						},
					},
					component: { props: { color: 'auto' } }, // 自动染色
				},
				city: {
					title: t('message.pages.loginLog.table.columns.city'),
					type: 'input',
					column:{
						minWidth: 80,
					},
					form: {
						component: {
							placeholder: t('message.pages.loginLog.form.cityPlaceholder'),
						},
					},
					component: { props: { color: 'auto' } }, // 自动染色
				},
				district: {
					title: t('message.pages.loginLog.table.columns.district'),
					key: '',
					type: 'input',
					column:{
						minWidth: 80,
					},
					form: {
						component: {
							placeholder: t('message.pages.loginLog.form.districtPlaceholder'),
						},
					},
					component: { props: { color: 'auto' } }, // 自动染色
				},
				area_code: {
					title: t('message.pages.loginLog.table.columns.areaCode'),
					type: 'input',
					column:{
						minWidth: 90,
					},
					form: {
						component: {
							placeholder: t('message.pages.loginLog.form.areaCodePlaceholder'),
						},
					},
					component: { props: { color: 'auto' } }, // 自动染色
				},
				country_english: {
					title: t('message.pages.loginLog.table.columns.countryEnglish'),
					type: 'input',
					column:{
						minWidth: 120,
					},
					form: {
						component: {
							placeholder: t('message.pages.loginLog.form.countryEnglishPlaceholder'),
						},
					},
					component: { props: { color: 'auto' } }, // 自动染色
				},
				country_code: {
					title: t('message.pages.loginLog.table.columns.countryCode'),
					type: 'input',
					column:{
						minWidth: 100,
					},
					form: {
						component: {
							placeholder: t('message.pages.loginLog.form.countryCodePlaceholder'),
						},
					},
					component: { props: { color: 'auto' } }, // 自动染色
				},
				longitude: {
					title: t('message.pages.loginLog.table.columns.longitude'),
					type: 'input',
					disabled: true,
					column:{
						minWidth: 100,
					},
					form: {
						component: {
							placeholder: t('message.pages.loginLog.form.longitudePlaceholder'),
						},
					},
					component: { props: { color: 'auto' } }, // 自动染色
				},
				latitude: {
					title: t('message.pages.loginLog.table.columns.latitude'),
					type: 'input',
					disabled: true,
					column:{
						minWidth: 100,
					},
					form: {
						component: {
							placeholder: t('message.pages.loginLog.form.latitudePlaceholder'),
						},
					},
					component: { props: { color: 'auto' } }, // 自动染色
				},
				login_type: {
					title: t('message.pages.loginLog.table.columns.loginType'),
					type: 'dict-select',
					search: {
						disabled: false,
					},
					dict: dict({
						data: [
							{ label: t('message.pages.loginLog.loginType.normal'), value: 1 },
							{ label: t('message.pages.loginLog.loginType.wechat'), value: 2 },
						],
					}),
					column:{
						minWidth: 120,
					},
					form: {
						component: {
							placeholder: t('message.pages.loginLog.form.loginTypePlaceholder'),
						},
					},
				},
				os: {
					title: t('message.pages.loginLog.table.columns.os'),
					type: 'input',
					column:{
						minWidth: 120,
					},
					form: {
						component: {
							placeholder: t('message.pages.loginLog.form.osPlaceholder'),
						},
					},
				},
				browser: {
					title: t('message.pages.loginLog.table.columns.browser'),
					type: 'input',
					column:{
						minWidth: 120,
					},
					form: {
						component: {
							placeholder: t('message.pages.loginLog.form.browserPlaceholder'),
						},
					},
				},
				agent: {
					title: t('message.pages.loginLog.table.columns.agent'),
					disabled: true,
					type: 'input',
					column:{
						minWidth: 120,
					},
					form: {
						component: {
							placeholder: t('message.pages.loginLog.form.agentPlaceholder'),
						},
					},
				},
				...commonCrudConfig({
					create_datetime: {
						search: true
					}
				}, t)
			},
		},
	};
};
