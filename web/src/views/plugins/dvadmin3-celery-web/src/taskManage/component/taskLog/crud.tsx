import * as api from './api';
import { dict, UserPageQuery, AddReq, DelReq, EditReq, compute, CreateCrudOptionsProps, CreateCrudOptionsRet } from '@fast-crud/fast-crud';

export const createCrudOptions = function ({ crudExpose, context }: CreateCrudOptionsProps): CreateCrudOptionsRet {
	const pageRequest = async (query: UserPageQuery) => {
		return await api.GetList({ ...query, ...{ name: context!.taskItem.name } });
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
			actionbar: {
				show: false,
			},
			toolbar: {
				show: false,
			},
			request: {
				pageRequest,
				addRequest,
				editRequest,
				delRequest,
			},
			rowHandle: {
				show: false,
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
				task_id: {
					title: '任务ID',
					search: { show: true },
					type: 'text',
				},
				periodic_task_name: {
					title: '任务名称',
					search: { show: true },
					type: 'text',
				},
				status: {
					title: '执行状态',
					search: { show: true },
					type: 'dict-select',
					dict: dict({
						data: [
							{
								label: '执行成功',
								value: 'SUCCESS',
								color: 'success',
								effect: 'dark',
							},
							{
								label: '已开始',
								value: 'STARTED',
								effect: 'dark',
							},
							{
								label: '已取消',
								value: 'REVOKED',
								effect: 'dark',
							},
							{
								label: '重试中',
								value: 'RETRY',
								effect: 'dark',
							},
							{
								label: '已收到',
								value: 'RECEIVED',
								effect: 'dark',
							},
							{
								label: '待定中',
								value: 'PENDING',
								effect: 'dark',
							},
							{
								label: '执行失败',
								value: 'FAILURE',
								effect: 'dark',
								color: 'error',
							},
						],
					}),
				},
				result: {
					title: '执行结果',
					column: {
						showOverflowTooltip: true,
					},
				},
			},
		},
	};
};
