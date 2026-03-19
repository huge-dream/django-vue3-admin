import {dict} from '@fast-crud/fast-crud';
import {shallowRef} from 'vue';
import deptFormat from '/@/components/dept-format/index.vue';

/** 1. 每个字段可选属性 */
export interface CrudFieldOption {
	form?: boolean;
	table?: boolean;
	search?: boolean;
	width?: number;
}

/** 2. 总配置接口 */
export interface CrudOptions {
	create_datetime?: CrudFieldOption;
	update_datetime?: CrudFieldOption;
	creator_name?: CrudFieldOption;
	modifier_name?: CrudFieldOption;
	dept_belong_id?: CrudFieldOption;
	description?: CrudFieldOption;
}

/** 3. 默认完整配置 */
const defaultOptions: Required<CrudOptions> = {
	create_datetime: { form: false, table: false, search: false, width: 160 },
	update_datetime: { form: false, table: false, search: false, width: 160 },
	creator_name: { form: false, table: false, search: false, width: 100 },
	modifier_name: { form: false, table: false, search: false, width: 100 },
	dept_belong_id: { form: false, table: false, search: false, width: 300 },
	description: { form: false, table: false, search: false, width: 100 },
};

/** 4. mergeOptions 函数 */
function mergeOptions(baseOptions: Required<CrudOptions>, userOptions: CrudOptions = {}): Required<CrudOptions> {
	const result = { ...baseOptions };
	for (const key in userOptions) {
		if (Object.prototype.hasOwnProperty.call(userOptions, key)) {
			const baseField = result[key as keyof CrudOptions];
			const userField = userOptions[key as keyof CrudOptions];
			if (baseField && userField) {
				result[key as keyof CrudOptions] = { ...baseField, ...userField };
			}
		}
	}
	return result;
}

/**
 * 最终暴露的 commonCrudConfig
 * @param options 用户自定义配置（可传可不传，不传就用默认）
 */
export const commonCrudConfig = (options: CrudOptions = {}) => {
	// ① 合并
	const merged = mergeOptions(defaultOptions, options);

	// ② 用 merged 中的值生成真正的 CRUD 配置
	return {
		dept_belong_id: {
			title: '所属部门',
			type: 'dict-tree',
			search: {
				show: merged.dept_belong_id.search,
			},
			dict: dict({
				url: '/api/system/dept/all_dept/',
				isTree: true,
				value: 'id',
				label: 'name',
				children: 'children',
			}),
			column: {
				align: 'center',
				width: merged.dept_belong_id.width,
				show: merged.dept_belong_id.table,
				component: {
					// fast-crud里自定义组件常用"component.is"
					is: shallowRef(deptFormat),
					vModel: 'modelValue',
				},
			},
			form: {
				show: merged.dept_belong_id.form,
				component: {
					multiple: false,
					clearable: true,
					props: {
						checkStrictly: true,
						props: {
							label: 'name',
							value: 'id',
						},
					},
				},
				helper: '默认不填则为当前创建用户的部门ID',
			},
		},
		description: {
			title: '备注',
			search: {
				show: merged.description.search,
			},
			type: 'textarea',
			column: {
				width: merged.description.width,
				show: merged.description.table,
			},
			form: {
				show: merged.description.form,
				component: {
					placeholder: '请输入内容',
					showWordLimit: true,
					maxlength: '200',
				},
			},
			viewForm: {
				show: true,
			},
		},

		modifier_name: {
			title: '修改人',
			search: {
				show: merged.modifier_name.search,
			},
			column: {
				width: merged.modifier_name.width,
				show: merged.modifier_name.table,
			},
			form: {
				show: merged.modifier_name.form,
			},
			viewForm: {
				show: true,
			},
		},

		creator_name: {
			title: '创建人',
			search: {
				show: merged.creator_name.search,
			},
			column: {
				width: merged.creator_name.width,
				show: merged.creator_name.table,
			},
			form: {
				show: merged.creator_name.form,
			},
			viewForm: {
				show: true,
			},
		},

		update_datetime: {
			title: '更新时间',
			type: 'datetime',
			search: {
				show: merged.update_datetime.search,
				col: { span: 8 },
				component: {
					type: 'datetimerange',
					props: {
						'start-placeholder': '开始时间',
						'end-placeholder': '结束时间',
						'value-format': 'YYYY-MM-DD HH:mm:ss',
						'picker-options': {
							shortcuts: [
								{
									text: '最近一周',
									onClick(picker: any) {
										const end = new Date();
										const start = new Date();
										start.setTime(start.getTime() - 3600 * 1000 * 24 * 7);
										picker.$emit('pick', [start, end]);
									},
								},
								{
									text: '最近一个月',
									onClick(picker: any) {
										const end = new Date();
										const start = new Date();
										start.setTime(start.getTime() - 3600 * 1000 * 24 * 30);
										picker.$emit('pick', [start, end]);
									},
								},
								{
									text: '最近三个月',
									onClick(picker: any) {
										const end = new Date();
										const start = new Date();
										start.setTime(start.getTime() - 3600 * 1000 * 24 * 90);
										picker.$emit('pick', [start, end]);
									},
								},
							],
						},
					},
				},
				valueResolve(context: any) {
					const { value } = context;
					if (value) {
						context.form.update_datetime_after = value[0];
						context.form.update_datetime_before = value[1];
						delete context.form.update_datetime;
					}
				},
			},
			column: {
				width: merged.update_datetime.width,
				show: merged.update_datetime.table,
			},
			form: {
				show: merged.update_datetime.form,
			},
			viewForm: {
				show: true,
			},
		},

		create_datetime: {
			title: '创建时间',
			type: 'datetime',
			search: {
				show: merged.create_datetime.search,
				col: { span: 8 },
				component: {
					type: 'datetimerange',
					props: {
						'start-placeholder': '开始时间',
						'end-placeholder': '结束时间',
						'value-format': 'YYYY-MM-DD HH:mm:ss',
						'picker-options': {
							shortcuts: [
								{
									text: '最近一周',
									onClick(picker: any) {
										const end = new Date();
										const start = new Date();
										start.setTime(start.getTime() - 3600 * 1000 * 24 * 7);
										picker.$emit('pick', [start, end]);
									},
								},
								{
									text: '最近一个月',
									onClick(picker: any) {
										const end = new Date();
										const start = new Date();
										start.setTime(start.getTime() - 3600 * 1000 * 24 * 30);
										picker.$emit('pick', [start, end]);
									},
								},
								{
									text: '最近三个月',
									onClick(picker: any) {
										const end = new Date();
										const start = new Date();
										start.setTime(start.getTime() - 3600 * 1000 * 24 * 90);
										picker.$emit('pick', [start, end]);
									},
								},
							],
						},
					},
				},
				valueResolve(context: any) {
					const { value } = context;
					if (value) {
						context.form.create_datetime_after = value[0];
						context.form.create_datetime_before = value[1];
						delete context.form.create_datetime;
					}
				},
			},
			column: {
				width: merged.create_datetime.width,
				show: merged.create_datetime.table,
			},
			form: {
				show: merged.create_datetime.form,
			},
			viewForm: {
				show: true,
			},
		},
	};
};
