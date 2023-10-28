import * as api from './api';
import { dict, UserPageQuery, AddReq, DelReq, EditReq, compute, CreateCrudOptionsProps, CreateCrudOptionsRet } from '@fast-crud/fast-crud';
import { request } from '/@/utils/service';
import { dictionary } from '/@/utils/dictionary';
import { successMessage } from '/@/utils/message';
import {inject} from "vue";

export const createCrudOptions = function ({ crudExpose,propsContext }: CreateCrudOptionsProps): CreateCrudOptionsRet {
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
		form.role = propsContext.roleId
		return await api.AddObj(form);
	};

	//权限判定
	const hasPermissions = inject("$hasPermissions")

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
				name:{
					title: '接口名称',
					type: 'text',
					search:{
						show:true
					},
					column:{
						width:150
					}
				},
				method: {
					title: '请求方式',
					sortable: 'custom',
					search: {
						show:true
					},
					type: 'dict-select',
					dict: dict({
						data: [
							{
								label: 'GET',
								value: 0,
							},
							{
								label: 'POST',
								value: 1,
							},
							{
								label: 'PUT',
								value: 2,
							},
							{
								label: 'DELETE',
								value: 3,
							},
							{
								label: 'PATCH',
								value: 4,
							},
						],
					}),
					column:{
						width: 100,
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
						},
					},
				},
				api: {
					title: '接口地址',
					sortable: 'custom',
					search: {
						disabled: true,
					},
					type: 'dict-select',
					dict: dict({
						async getData(dict: any) {
							return request('/swagger.json').then((ret: any) => {
								const res = Object.keys(ret.paths);
								const data = [];
								for (const item of res) {
									const obj = { label: '', value: '' };
									obj.label = item;
									obj.value = item;
									data.push(obj);
								}
								return data;
							});
						},
					}),
					column:{
						minWidth: 200,
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
							span: 24,
							props: {
								allowCreate: true,
								filterable: true,
								clearable: true,
							},
						},
						helper: {
							position: 'label',
							tooltip: {
								placement: 'top-start',
							},
							text: '请正确填写，以免请求时被拦截。匹配单例使用正则,例如:/api/xx/.*?/',
						},
					},
				},
				data_range: {
					title: '数据权限范围',
					search: {
						show:true
					},
					type: 'dict-select',
					dict:dict({
						url:'/api/system/role_api_permission/data_scope/'
					}),
					column: {
						minWidth:120,
					},

				},
				dept:{
					title:'数据权限部门',
					column:{
						minWidth:120,
					},
					form:{
						show: compute(({form})=>{
							return form.data_range===4
						})
					}
				},
				description:{
					title:'描述',
					type:'textarea',
					column:{
						width:300
					}
				}
			},
		},
	};
};
