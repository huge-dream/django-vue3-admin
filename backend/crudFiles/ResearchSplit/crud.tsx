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
                        show: auth("ResearchSplit:Update")
                    },
                    remove: {
                        iconRight: 'Delete',
                        type: 'text',
                        show: auth("ResearchSplit:Delete")
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
                search: {
                    title: '关键词',
                    column: {
                        show: false,
                    },
                    search: {
                        show: true,
                        component: {
                            props: {
                                clearable: true,
                            },
                            placeholder: '请输入关键词',
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
                id: {
                   title:"Id",
                   type:"unknown",
                   
                },description: {
                   title:"描述",
                   type:"text",
                   
                },creator: {
                   title:"创建人",
                   type:"unknown",
                   
                },modifier: {
                   title:"修改人",
                   type:"text",
                   
                },dept_belong_id: {
                   title:"数据归属部门",
                   type:"text",
                   
                },update_datetime: {
                   title:"修改时间",
                   type:"datetime",
                   
                },create_datetime: {
                   title:"创建时间",
                   type:"datetime",
                   
                },game: {
                   title:"游戏名称",
                   type:"unknown",
                   
                },research: {
                   title:"研发名称",
                   type:"unknown",
                   
                },research_ratio: {
                   title:"研发分成比例",
                   type:"number",
                   
                },slotting_ratio: {
                   title:"通道费比例",
                   type:"number",
                   
                },research_tips: {
                   title:"分成备注",
                   type:"textarea",
                   
                },
            },
        },
    };

}