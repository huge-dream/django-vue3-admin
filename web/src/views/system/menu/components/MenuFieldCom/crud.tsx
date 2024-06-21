import * as api from './api';
import { dict, UserPageQuery, AddReq, DelReq, EditReq, compute, CreateCrudOptionsProps, CreateCrudOptionsRet } from '@fast-crud/fast-crud';
import { request } from '/@/utils/service';
import { dictionary } from '/@/utils/dictionary';
import { inject } from 'vue';
import {auth} from "/@/utils/authFunction";
import { useI18n } from "vue-i18n";

export const createCrudOptions = function ({ crudExpose, props,modelDialog,selectOptions,allModelData }: CreateCrudOptionsProps): CreateCrudOptionsRet {
	const pageRequest = async (query: UserPageQuery) => {
		// return await api.GetList(query);
		if (selectOptions.value.id) {
			return await api.GetList({ menu: selectOptions.value.id } as any);
		} else {
			return undefined;
		}
	};
	const editRequest = async ({ form, row }: EditReq) => {
		form.id = row.id;
		return await api.UpdateObj(form);
	};
	const delRequest = async ({ row }: DelReq) => {
		return await api.DelObj(row.id);
	};
	const addRequest = async ({ form }: AddReq) => {
		form.menu = selectOptions.value.id;
		return await api.AddObj(form);
	};

    const { t } = useI18n();

    return {
        crudOptions: {
            request: {
                pageRequest,
                addRequest,
                editRequest,
                delRequest,
            },
            pagination: {
                show: false,
            },
            search: {
                container: {
                    action: {
                        //按钮栏配置
                        col: {
                            span: 8,
                        },
                    },
                },
            },
            actionbar: {
                buttons: {
                    add:{
                        // text: '增加',
                        show:auth('column:Create')
                    },
                    auto: {
                        // text: '自动匹配',
                        text: t("message.permission.auto"),
                        type: 'success',
                        show:auth('column:Match'),
                        click: () => {
                            return modelDialog.value=true;
                        },
                    },
                },
            },
            rowHandle: {
                //固定右侧
                fixed: 'right',
                buttons: {
                    view: {
                        show: false,
                    },
                    edit: {
                        show: auth('column:Update')
                    },
                    remove: {
                        show: auth('column:Delete')
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
                    // title: '序号',
                    title: t("message.permission.serial"),
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
                model: {
                    title: 'model',
                    type: 'dict-select',
                    dict:dict({
                        url:'/api/system/column/get_models/',
                        label:'title',
                        value:'key'
                    }),
                    column:{
                        sortable: true,
                    },
                    form: {
                        // 表单校验规则
                        rules: [{required: true, message: '必填项'}],
                        component: {
                            span: 12,
                            showSearch: true,
                            filterable: true,
                            //默认的filterOption仅支持value的过滤，label并不会加入查询
                            //所以需要自定义filterOption
                            filterOption(inputValue, option) {
                                return option.label.indexOf(inputValue) >= 0 || option.value.indexOf(inputValue) >= 0;
                            }
                        },
                    },
                },
                title: {
                    // title: '中文名',
                    title: t("message.permission.zhName"),
                    sortable: 'custom',
                    search: {
                        show: true,
                    },
                    type: 'text',
                    form: {
                        // 表单校验规则
                        rules: [{required: true, message: '必填项'}],
                        component: {
                            span: 12,
                            placeholder: '请输入中文名',
                        },
                    },
				},
                field_name: {
                    // title: '字段名',
                    title: t("message.permission.field"),
                    type: 'text',
                    search: {
                        show: true,
                    },
                    column:{
                        minWidth: 120,
                        sortable: true,
                    },
                    form: {
                        // 表单校验规则
                        rules: [{required: true, message: '必填项'}],
                        component: {
                            span: 12,
                            placeholder: '请输入字段名',
                        },
                        helper: {
                            render() {
                                return <el-alert title="手动输入" type="warning" description="页面中按钮的名称或者自定义一个名称"/>;
                            },
                        },
                    },
                },
            },
        },
    };
};
