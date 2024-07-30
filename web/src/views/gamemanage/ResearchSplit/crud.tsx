// ResearchSplit CRUD TypeScript - Auto-generated on 2024-05-20 13:56:12

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
// 注意：以下FastCrud配置应替换为实际的JavaScript/TypeScript代码片段
export const createCrudOptions = function ({crudExpose}: CreateCrudOptionsProps): CreateCrudOptionsRet {
    const pageRequest = async (query: UserPageQuery) => {
        const a = await api.GetList(query);
        console.log(a);
        return a;
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
                        show: auth('research_split_manage:Create')
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
                        show: auth("research_split_manage:Update")
                    },
                    remove: {
                        iconRight: 'Delete',
                        type: 'text',
                        show: auth("research_split_manage:Delete")
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
                    title: 'ID',
                    type: 'text',
                    form: {show: false},
                    column: {
                        show: false,
                    },
                }, game: {
                    title: "游戏名称",
                    type: "dict-select",
                    search: {
                        show: true,
                    },
                    column: {
                        show: false,
                    },
                    form: {
                        rules: [{required: true, message: '请输入游戏名称'}],
                        component: {
                            props: {
                                clearable: true,
                                filterable: true,
                            },
                        },
                    },
                    dict: dict({
                        url: '/api/game_manage/?page=1&limit=99999',
                        value: 'id',
                        label: 'name',
                    })
                }, game_name: {
                    title: "游戏名称",
                    type: "input",
                    column: {
                        align: 'center',
                        show: true,
                        width: 350,
                        showOverflowTooltip: true,
                    },
                    form: {
                        show: false
                    },
                }, research: {
                    title: "研发名称",
                    type: "dict-select",
                    search: {
                        show: true,
                    },
                    column: {
                        show: false,
                    },
                    form: {
                        rules: [{required: true, message: '请输入研发名称'}],
                        component: {
                            props: {
                                clearable: true,
                                filterable: true,
                            },
                        },
                    },
                    dict: dict({
                        url: '/api/research_manage/?page=1&limit=99999',
                        value: 'id',
                        label: 'name',
                    })
                }, research_name: {
                    title: "研发名称",
                    type: "input",
                    column: {
                        align: 'center',
                        show: true,
                        width: 150,
                    },
                    form: {
                        show: false
                    },
                }, game_release_date: {
                    title: "游戏发行日期",
                    type: "date",
                    search: {
                        show: true,
                    },
                    column: {
                        align: 'center',
                        sortable: true,
                        width: 150,
                    },
                    form: {
                        show: false
                    }
                }, research_ratio: {
                    title: "研发分成比例(%)",
                    type: "number",
                    search: {
                        show: true,
                    },
                    form: {
                        rules: [
                            {required: true, message: '请输入研发分成比例'},
                        ],
                        component: {
                            props: {
                                clearable: true,
                            },
                        }
                    },
                    column: {
                        align: 'center',
                        width: 150,
                    }
                }, slotting_ratio: {
                    title: "通道费比例(%)",
                    type: "number",
                    search: {
                        show: true,
                    },
                    form: {
                        rules: [
                            {required: true, message: '请输入通道费比例'},
                        ],
                        component: {
                            props: {
                                clearable: true,
                            },
                        }
                    },
                    column: {
                        align: 'center',
                        width: 150,
                    }
                }, research_tips: {
                    title: "分成备注",
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