import * as api from './api';
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
import {commonCrudConfig} from "/@/utils/commonCrud";

export const createCrudOptions = function ({crudExpose}: CreateCrudOptionsProps): CreateCrudOptionsRet {
    const pageRequest = async (query: UserPageQuery) => {
        const response = await api.GetList(query);
        // 对获取的数据进行处理，将 alias 列表转换为中文顿号分隔的字符串
        response.data.forEach((item: any) => {
            if (item.alias && Array.isArray(item.alias)) {
                item.alias = item.alias.join('、');
            }
        });
        return response;
    };

    const editRequest = async ({form, row}: EditReq) => {
        form.id = row.id;
        // 将渠道别名从字符串转换为列表
        if (form.alias) {
            form.alias = form.alias.split('、').map((item: string) => item.trim());
        }
        return await api.UpdateObj(form);
    };

    const delRequest = async ({row}: DelReq) => {
        return await api.DelObj(row.id);
    };

    const addRequest = async ({form}: AddReq) => {
        // 将渠道别名从字符串转换为列表
        if (form.alias) {
            form.alias = form.alias.split('、').map((item: string) => item.trim());
        }
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
                        show: auth('channel_manage:Create')
                    }
                }
            },
            rowHandle: {
                // 固定右侧
                fixed: 'right',
                width: 150,
                buttons: {
                    view: {
                        show: false,
                    },
                    edit: {
                        iconRight: 'Edit',
                        type: 'text',
                        show: auth("channel_manage:Update")
                    },
                    remove: {
                        iconRight: 'Delete',
                        type: 'text',
                        show: auth("channel_manage:Delete")
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
                    title: '序号',
                    form: {show: false},
                    column: {
                        type: 'index',
                        align: 'center',
                        width: '70px',
                        columnSetDisabled: true, // 禁止在列设置中选择
                    },
                },
                id: {
                    title: "Id",
                    type: "number",
                    form: {show: false},
                    column: {
                        show: false,
                    },
                },
                name: {
                    title: "渠道名称",
                    type: "input",
                    search: {
                        show: true,
                    },
                    column: {
                        align: 'center',
                        width: 200,
                    },
                    form: {
                        rules: [
                            {required: true, message: "请输入渠道名称"},
                        ],
                        component: {
                            props: {
                                clearable: true,
                            },
                        }
                    },
                },
                alias: {
                    title: "渠道别名",
                    type: "input",
                    form: {
                        rules: [
                            {required: true, message: "请输入渠道别名"},
                        ],
                        component: {
                            props: {
                                clearable: true,
                                placeholder: "请输入渠道别名，用中文顿号分隔"
                            },
                        }
                    },
                    column: {
                        maxWidth: 200,
                        showOverflowTooltip: true,
                    },
                },
                company_name: {
                    title: "渠道公司名",
                    type: "input",
                    search: {
                        show: true,
                    },
                    column: {
                        width: 250,
                        align: 'center',
                        showOverflowTooltip: true,
                    },
                    form: {
                        rules: [
                            {required: true, message: "请输入渠道公司名"},
                        ],
                        component: {
                            props: {
                                clearable: true,
                            },
                        }
                    },
                },
                our_ratio: {
                    title: "我方分成比例(%)",
                    type: "number",
                    search: {
                        show: true,
                    },
                    column: {
                        align: 'center',
                        width: 150,
                    },
                    form: {
                        rules: [
                            {required: true, message: "请输入我方分成比例"},
                        ],
                        component: {
                            props: {
                                clearable: true,
                            },
                        }
                    },
                },
                channel_ratio: {
                    title: "渠道分成比例(%)",
                    type: "number",
                    search: {
                        show: true,
                    },
                    column: {
                        align: 'center',
                        width: 150,
                    },
                    form: {
                        rules: [
                            {required: true, message: "请输入渠道分成比例"},
                        ],
                        component: {
                            props: {
                                clearable: true,
                            },
                        }
                    }
                },
                channel_fee_ratio: {
                    title: "渠道费比例(%)",
                    type: "number",
                    search: {
                        show: true,
                    },
                    column: {
                        align: 'center',
                        width: 150,
                    },
                    form: {
                        rules: [
                            {required: true, message: "请输入渠道费比例"},
                        ],
                        component: {
                            props: {
                                clearable: true,
                            },
                        }
                    }
                },
                channel_tips: {
                    title: "渠道备注",
                    type: "textarea",
                    column: {
                        align: 'center',
                        showOverflowTooltip: true,
                    }
                }, status: {
                    title: "渠道状态",
                    search: {
                        show: true,
                    },
                    type: 'dict-radio',
                    column: {
                        width: 120,
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
                        data: dictionary('button_status_number'),
                    }),
                },
                ...commonCrudConfig(

                )
            },
        },
    };
}
