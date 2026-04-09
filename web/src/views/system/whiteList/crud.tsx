import * as api from './api';
import { useI18n } from 'vue-i18n';
import {
    dict,
    UserPageQuery,
    AddReq,
    DelReq,
    EditReq,
    compute,
    CreateCrudOptionsProps,
    CreateCrudOptionsRet
} from '@fast-crud/fast-crud';
import {request} from '/@/utils/service';
import {dictionary} from '/@/utils/dictionary';
import {successMessage} from '/@/utils/message';
import {auth} from '/@/utils/authFunction'

export const createCrudOptions = function ({crudExpose}: CreateCrudOptionsProps): CreateCrudOptionsRet {
	const { t } = useI18n()
    const pageRequest = async (query: UserPageQuery) => {
        return await api.GetList(query);
    };
    const editRequest = async ({form, row}: EditReq) => {
        form.id = row.id;
        return await api.UpdateObj(form);
    };
    const delRequest = async ({row}: DelReq) => {
        return await api.DelObj(row.id);
    };
    const addRequest = async ({form}: AddReq) => {
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
                        show: auth('api_white_list:Create')
                    }
                }
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
                        show: auth("api_white_list:Update")
                    },
                    remove: {
                        iconRight: 'Delete',
                        type: 'text',
                        show: auth("api_white_list:Delete")
                    },
                },
            },
            form: {
                col: {span: 24},
                labelWidth: '110px',
                wrapper: {
                    is: 'el-dialog',
                    width: '600px',
                },
            },
            columns: {
                _index: {
                    title: t('message.pages.whitelist.table.columns.index'),
                    form: {show: false},
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
                search: {
                    title: t('message.pages.whitelist.table.columns.keyword'),
                    column: {
                        show: false,
                    },
                    search: {
                        show: true,
                        component: {
                            props: {
                                clearable: true,
                            },
                            placeholder: t('message.pages.whitelist.form.keywordPlaceholder'),
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
                method: {
                    title: t('message.pages.whitelist.table.columns.method'),
                    sortable: 'custom',
                    search: {
                        disabled: false,
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
                    column: {
                        minWidth: 120,
                    },
                    form: {
                        rules: [
                            // 表单校验规则
                            {
                                required: true,
                                message: t('message.pages.whitelist.validation.methodRequired'),
                            },
                        ],
                        component: {
                            span: 12,
                        },
                        itemProps: {
                            class: {yxtInput: true},
                        },
                    },
                },
                url: {
                    title: t('message.pages.whitelist.table.columns.url'),
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
                                    const obj = {label: '', value: ''};
                                    obj.label = item;
                                    obj.value = item;
                                    data.push(obj);
                                }
                                return data;
                            });
                        },
                    }),
                    column: {
                        minWidth: 200,
                    },
                    form: {
                        rules: [
                            // 表单校验规则
                            {
                                required: true,
                                message: t('message.pages.whitelist.validation.urlRequired'),
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
                        itemProps: {
                            class: {yxtInput: true},
                        },
                        helper: {
                            position: 'label',
                            tooltip: {
                                placement: 'top-start',
                            },
                            text: t('message.pages.whitelist.form.urlHelper'),
                        },
                    },
                },
                enable_datasource: {
                    title: t('message.pages.whitelist.table.columns.dataPermission'),
                    search: {
                        disabled: false,
                    },
                    type: 'dict-radio',
                    column: {
                        minWidth: 120,
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
