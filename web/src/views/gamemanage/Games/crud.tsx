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
import {dictionary} from '/@/utils/dictionary';
import {successMessage} from '/@/utils/message';
import {auth} from "/@/utils/authFunction";
import {commonCrudConfig} from "/@/utils/commonCrud";

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
                        show: auth('game_manage:Create')
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
                        show: auth("game_manage:Update")
                    },
                    remove: {
                        iconRight: 'Delete',
                        type: 'text',
                        show: auth("game_manage:Delete")
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
                id: {
                    title: "Id",
                    type: "number",
                    form: {show: false},
                    column: {
                        show: false,
                    },

                }, name: {
                    title: "上线名称",
                    type: "input",
                    search: {
                        show: true,
                    },
                    column: {
                        align: 'center',
                        width: 300,
                        showOverflowTooltip: true,
                    },
                    form: {
                        rules: [
                            {required: true, message: '请输入游戏上线名称'},
                        ],
                        component: {
                            props: {
                                clearable: true,
                            },
                        },
                    },

                }, quick_name: {
                    title: "Quick名称",
                    type: "input",
                    search: {
                        show: true,
                    },
                    column: {
                        // align: 'center',
                        // width: 300,
                        // showOverflowTooltip: true,
                        show: false,
                    },
                    form: {
                        rules: [
                            {required: true, message: '请输入游戏Quick名称'},
                        ],
                        component: {
                            props: {
                                clearable: true,
                            },
                        }
                    },
                }, release_date: {
                    title: "发行日期",
                    type: "date",
                    column: {
                        align: 'center',
                        sortable: true,
                        width: 120,
                    },
                    form: {
                        component: {
                            props: {
                                format: 'YYYY-MM-DD',
                                valueFormat: 'YYYY-MM-DD'
                            }
                        }
                    }
                }, stop_add_date: {
                    title: "停新增日期",
                    type: "date",
                    column: {
                        align: 'center',
                        sortable: true,
                        width: 120,
                    },
                    form: {
                        component: {
                            props: {
                                format: 'YYYY-MM-DD',
                                valueFormat: 'YYYY-MM-DD'
                            }
                        }
                    }
                }, stop_operation_date: {
                    title: "停运营日期",
                    type: "date",
                    column: {
                        align: 'center',
                        sortable: true,
                        width: 120,
                    },
                    form: {
                        component: {
                            props: {
                                format: 'YYYY-MM-DD',
                                valueFormat: 'YYYY-MM-DD'
                            }
                        }
                    }
                },
                parent: {
                    title: "发行主体",
                    type: "select",
                    column: {
                        align: 'center',
                        width: 100,
                    },
                    form: {
                        rules: [
                            {required: true, message: '请输入发行主体'},
                        ],
                        component: {
                            props: {
                                clearable: true,
                                filterable: true,
                            },
                        },
                    },
                }, discount: {
                    title: "折算比例",
                    type: "number",
                    search: {
                        show: true,
                    },
                    column: {
                        align: 'center',
                        width: 100,
                    }
                }, type: {
                    title: "游戏类型",
                    type: "input",
                    column: {
                        align: 'center',
                        width: 100,
                    },
                }, issue: {
                    title: "发行类型",
                    type: "input",
                    column: {
                        align: 'center',
                        width: 100,
                    },
                }, reconciliation_ratio: {
                    title: "对账比例",
                    type: "number",
                    search: {
                        show: true,
                    },
                    column: {
                        align: 'center',
                        width: 100,
                    },
                }, status: {
                    title: "游戏状态",
                    type: 'dict-select',
                    search: {
                        show: true,
                    },
                    column: {
                        align: 'center',
                        width: 100,
                    },
                    dict: dict({
                        data: dictionary('game_status'),
                        label: "label",
                        value: "value"
                    }),
                }, desc: {
                    title: "描述",
                    type: "textarea",
                    column: {
                        align: 'center',
                        showOverflowTooltip: true,
                    }
                },
                ...commonCrudConfig()
            },
        },
    };

}
