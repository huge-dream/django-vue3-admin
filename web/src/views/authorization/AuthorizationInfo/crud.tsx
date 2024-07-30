// AuthorInfo CRUD TypeScript - Auto-generated on 2024-05-12 23:12:04

import * as api from './api';
import {
    AddReq,
    CreateCrudOptionsProps,
    CreateCrudOptionsRet,
    DelReq, dict,
    EditReq,
    UserPageQuery
} from '@fast-crud/fast-crud';
import {auth} from '/@/utils/authFunction'
import {commonCrudConfig} from "/@/utils/commonCrud";
// 注意：以下FastCrud配置应替换为实际的JavaScript/TypeScript代码片段
export const createCrudOptions = function ({crudExpose}: CreateCrudOptionsProps): CreateCrudOptionsRet {
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
                        show: auth('authorletter_manage:Create')
                    }
                }
            },
            rowHandle: {
                //固定右侧
                fixed: 'right',
                align: 'center',
                width: 150,
                buttons: {
                    view: {
                        iconRight: 'View',
                        type: 'text',
                        show: auth("authorletter_manage:View"),
                    },
                    edit: {
                        iconRight: 'Edit',
                        type: 'text',
                        show: auth("authorletter_manage:Update")
                    },
                    remove: {
                        iconRight: 'Delete',
                        type: 'text',
                        show: auth("authorletter_manage:Delete")
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
                        columnSetDisabled: true, //禁止在列设置中选择
                    },
                },
                name: {
                    title: "版号",
                    type: "input",
                    search: {show: true, component: {props: {clearable: true}}},
                    column: {
                        width: 150,
                        align: 'center',
                    },
                    form: {
                        rules: [
                            {required: true, message: '请输入版号'},
                        ],
                        component: {
                            props: {
                                clearable: true,
                            },
                        },
                    },
                },
                entity: {
                    title: "主体",
                    type: "input",
                    column: {
                        width: 80, //最小列宽
                        align: 'center',
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
                        },
                    },
                    search: {show: true, component: {props: {clearable: true}}},
                },
                publisher: {
                    title: "出版社",
                    type: "text",
                    search: {show: true, component: {props: {clearable: true}}},
                    form: {
                        rules: [
                            {required: true, message: '请输入出版社'},
                        ],
                        component: {
                            props: {
                                clearable: true,
                            },
                        },
                    },
                    column: {
                        width: 200,
                        align: 'center',
                        showOverflowTooltip: true,
                    },
                },
                software_registration_number: {
                    title: "软著登记编号",
                    type: "text",
                    search: {show: true, component: {props: {clearable: true}}},
                    form: {
                        rules: [
                            {required: true, message: '请输入软著登记编号'},
                        ],
                        component: {
                            props: {
                                clearable: true,
                            },
                        },
                    },
                    column: {
                        width: 150,
                        align: 'center',
                        showOverflowTooltip: true,
                    }
                },
                isbn: {
                    title: "出版物号",
                    type: "text",
                    search: {show: true, component: {props: {clearable: true}}},
                    form: {
                        rules: [
                            {required: true, message: '请输入出版物号'},
                        ],
                        component: {
                            props: {
                                clearable: true,
                            },
                        },
                    },
                    column: {
                        width: 150,
                        align: 'center',
                        showOverflowTooltip: true,
                    }
                },
                publication_approval_number: {
                    title: "出版复批文号",
                    type: "text",
                    search: {show: true, component: {props: {clearable: true}}},
                    form: {
                        rules: [
                            {required: true, message: '请输入出版复批文号'},
                        ],
                        component: {
                            props: {
                                clearable: true,
                            },
                        },
                    },
                    column: {
                        width: 200,
                        align: 'center',
                        showOverflowTooltip: true,
                    }
                },
                authorization_start_date: {
                    title: "授权开始日期",
                    type: "date",
                    column: {
                        width: 140,
                        sortable: true,
                        format: "YYYY-MM-DD",
                        "value-format": "YYYY-MM-DD",
                    },
                    form: {
                        rules: [
                            {required: true, message: '请输入授权开始日期'},
                        ],
                        component: {
                            props: {
                                clearable: true,
                                format: "YYYY-MM-DD",
                                "value-format": "YYYY-MM-DD",
                            },
                        },
                    }
                },
                authorization_end_date: {
                    title: "授权结束日期",
                    type: "date",
                    column: {
                        width: 140,
                        sortable: true,
                        format: "YYYY-MM-DD",
                        "value-format": "YYYY-MM-DD",
                    },
                    form: {
                        rules: [
                            {required: true, message: '请输入授权结束日期'},
                        ],
                        component: {
                            props: {
                                clearable: true,
                                format: "YYYY-MM-DD",
                                "value-format": "YYYY-MM-DD",
                            },
                        },
                    }
                },
                icp_license: {
                    title: "Icp备案证书",
                    type: "text",
                    search: {show: true, component: {props: {clearable: true}}},
                    column: {
                        width: 200,
                        align: 'center',
                        showOverflowTooltip: true,
                    }
                },
                ...commonCrudConfig(),
            },
        },
    };

}