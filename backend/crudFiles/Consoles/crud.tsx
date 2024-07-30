// Consoles CRUD TypeScript - Auto-generated on 2024-07-12 13:49:43

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
                        show: auth("Consoles:Create")
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
                        show: auth("Consoles:Update")
                    },
                    remove: {
                        iconRight: 'Delete',
                        type: 'text',
                        show: auth("Consoles:Delete")
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
                   
                },account: {
                   title:"账号",
                   type:"unknown",
                   
                },instance_id: {
                   title:"实例Id",
                   type:"text",
                   
                },instance_name: {
                   title:"实例名称",
                   type:"text",
                   
                },status: {
                   title:"状态",
                   type:"text",
                   
                },instance_type_id: {
                   title:"规格",
                   type:"text",
                   
                },cpus: {
                   title:"Cpu",
                   type:"text",
                   
                },memory_size: {
                   title:"内存",
                   type:"text",
                   
                },eip_address: {
                   title:"主Ipv4地址",
                   type:"text",
                   
                },primary_ip_address: {
                   title:"次Ipv4地址",
                   type:"text",
                   
                },instance_charge_type: {
                   title:"实例计费类型",
                   type:"text",
                   
                },expired_at: {
                   title:"到期时间",
                   type:"text",
                   
                },
            },
        },
    };

}