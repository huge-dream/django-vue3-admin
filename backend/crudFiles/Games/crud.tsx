// Games CRUD TypeScript - Auto-generated on 2024-05-20 15:28:49

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
                        show: auth("Games:Update")
                    },
                    remove: {
                        iconRight: 'Delete',
                        type: 'text',
                        show: auth("Games:Delete")
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
                   
                },name: {
                   title:"游戏上线名称",
                   type:"text",
                   
                },quick_name: {
                   title:"游戏Quick名称",
                   type:"text",
                   
                },type: {
                   title:"游戏类型",
                   type:"select",
                   dict:dict({
                     data:[{'label': '常规', 'value': 0}, {'label': 'BT版', 'value': 1}, {'label': '外置0.1折', 'value': 2}, {'label': '内置0.1折', 'value': 3}, {'label': '外置0.05折', 'value': 4}, {'label': '内置0.05折', 'value': 5}],
                     label:"label",
                     value:"value"
                   })
                },release_date: {
                   title:"游戏发行时间",
                   type:"unknown",
                   
                },parent: {
                   title:"游戏发行主体",
                   type:"unknown",
                   
                },status: {
                   title:"游戏状态",
                   type:"select",
                   dict:dict({
                     data:[{'label': '未上线', 'value': 0}, {'label': '已上线', 'value': 1}, {'label': '已下架', 'value': 2}, {'label': '已关服', 'value': 3}],
                     label:"label",
                     value:"value"
                   })
                },issue: {
                   title:"游戏发行类型",
                   type:"select",
                   dict:dict({
                     data:[{'label': '大混服', 'value': 0}, {'label': '小混服', 'value': 1}, {'label': '专服', 'value': 2}],
                     label:"label",
                     value:"value"
                   })
                },desc: {
                   title:"游戏描述",
                   type:"textarea",
                   
                },
            },
        },
    };

}