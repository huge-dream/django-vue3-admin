// Leave CRUD TypeScript - Auto-generated on 2024-05-09 16:07:18

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
                        show: auth("Leave:Update")
                    },
                    remove: {
                        iconRight: 'Delete',
                        type: 'text',
                        show: auth("Leave:Delete")
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
                   
                },leave_type: {
                   title:"请假类型",
                   type:"select",
                   dict:dict({
                     data:[{'label': '事假', 'value': 0}, {'label': '病假', 'value': 1}, {'label': '年假', 'value': 2}, {'label': '调休', 'value': 3}, {'label': '婚假', 'value': 4}, {'label': '产假', 'value': 5}, {'label': '陪产假', 'value': 6}, {'label': '丧假', 'value': 7}, {'label': '其他', 'value': 8}],
                     label:"label",
                     value:"value"
                   })
                },start_time: {
                   title:"请假开始时间",
                   type:"datetime",
                   
                },end_time: {
                   title:"请假结束时间",
                   type:"datetime",
                   
                },reason: {
                   title:"请假原因",
                   type:"textarea",
                   
                },duration: {
                   title:"请假时长",
                   type:"number",
                   
                },status: {
                   title:"请假状态",
                   type:"select",
                   dict:dict({
                     data:[{'label': '待审批', 'value': 0}, {'label': '已通过', 'value': 1}, {'label': '驳回', 'value': 2}],
                     label:"label",
                     value:"value"
                   })
                },
            },
        },
    };

}