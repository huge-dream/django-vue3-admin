import * as api from './api';
import { dict, UserPageQuery, AddReq, DelReq, EditReq, compute, CreateCrudOptionsProps, CreateCrudOptionsRet } from '@fast-crud/fast-crud';
import { request } from '/@/utils/service';
import { dictionary } from '/@/utils/dictionary';
import { successMessage } from '/@/utils/message';
import { inject } from 'vue';
import {auth} from "/@/utils/authFunction";
import {commonCrudConfig} from "/@/utils/commonCrud";

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
			rowHandle: {
				//固定右侧
				fixed: 'right',
				width: 150,
				buttons: {
					view: {
						show: false,
					},
					edit: {
						iconRight: 'Edit',
						type: 'text',
						// @ts-ignore
						show: auth('api_white_list:Update'),
					},
					remove: {
						iconRight: 'Delete',
						type: 'text',
						// @ts-ignore
						show: auth('api_white_list:Delete'),
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

				minute: {
					title: 'minute',
					sortable: 'custom',
					type: 'text',
				},
				hour: {
					title: 'hour',
					sortable: 'custom',
					type: 'text',
				},
				day_of_week: {
					title: 'day_of_week',
					sortable: 'custom',
					type: 'text',
				},
				day_of_month: {
					title: 'day_of_month',
					sortable: 'custom',
					type: 'text',
				},
				month_of_year: {
					title: 'month_of_year',
					sortable: 'custom',
					type: 'text',
				},
			},
		},
	};
};
