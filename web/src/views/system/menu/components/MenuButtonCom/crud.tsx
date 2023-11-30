import {AddReq, DelReq, EditReq, dict, CreateCrudOptionsRet, CreateCrudOptionsProps} from '@fast-crud/fast-crud';
import * as api from './api';
import {auth} from '/@/utils/authFunction'
import {request} from '/@/utils/service';
//此处为crudOptions配置
export const createCrudOptions = function ({crudExpose, context}: CreateCrudOptionsProps): CreateCrudOptionsRet {
    const pageRequest = async () => {
        if (context!.selectOptions.value.id) {
            return await api.GetList({menu: context!.selectOptions.value.id} as any);
        } else {
            return undefined;
        }
    };
    const editRequest = async ({form, row}: EditReq) => {
        return await api.UpdateObj({...form, menu: row.menu});
    };
    const delRequest = async ({row}: DelReq) => {
        return await api.DelObj(row.id);
    };
    const addRequest = async ({form}: AddReq) => {
        return await api.AddObj({...form, ...{menu: context!.selectOptions.value.id}});
    };
    return {
        crudOptions: {
            pagination:{
                show:false
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
                    add: {
                        show: auth('btn:Create')
                    },
                },
            },
            rowHandle: {
                //固定右侧
                fixed: 'right',
                width: 200,
                buttons: {
                    view: {
                        show: false,
                    },
                    edit: {
                        icon: '',
                        type: 'primary',
                        show: auth('btn:Update')
                    },
                    remove: {
                        show: auth('btn:Delete')
                    },
                },
            },
            request: {
                pageRequest,
                addRequest,
                editRequest,
                delRequest,
            },
            form: {
                col: {span: 24},
                labelWidth: '100px',
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
                    column: {show: false},
                    type: 'text',
                    search: {show: true},
                    form: {
                        show: false,
                        component: {
                            placeholder: '输入关键词搜索',
                        },
                    },
                },
                id: {
                    title: 'ID',
                    type: 'text',
                    column: {show: false},
                    search: {show: false},
                    form: {show: false},
                },
                name: {
                    title: '权限名称',
                    type: 'text',
                    search: {show: true},
                    column: {
                        minWidth: 120,
                        sortable: true,
                    },
                    form: {
                        rules: [{required: true, message: '权限名称必填'}],
                        component: {
                            placeholder: '输入权限名称搜索',
                            props: {
                                clearable: true,
                                allowCreate: true,
                                filterable: true,
                            },
                        },
                        helper: {
                            render() {
                                return <el-alert title="手动输入" type="warning"
                                                 description="页面中按钮的名称或者自定义一个名称"/>;
                            },
                        },
                    },
                },
                value: {
                    title: '权限值',
                    type: 'text',
                    search: {show: false},
                    column: {
                        width: 200,
                        sortable: true,
                    },
                    form: {
                        rules: [{required: true, message: '权限标识必填'}],
                        placeholder: '输入权限标识',
                        helper: {
                            render() {
                                return <el-alert title="唯一值" type="warning"
                                                 description="用于判断前端按钮权限或接口权限"/>;
                            },
                        },
                    },
                },
                method: {
                    title: '请求方式',
                    search: {show: false},
                    type: 'dict-select',
                    column: {
                        width: 120,
                        sortable: true,
                    },
                    dict: dict({
                        data: [
                            {label: 'GET', value: 0},
                            {label: 'POST', value: 1, color: 'success'},
                            {label: 'PUT', value: 2, color: 'warning'},
                            {label: 'DELETE', value: 3, color: 'danger'},
                        ],
                    }),
                    form: {
                        rules: [{required: true, message: '必填项'}],
                    },
                },
                api: {
                    title: '接口地址',
                    search: {show: false},
                    type: 'dict-select',
                    dict: dict({
                        getData() {
                            return request({url: '/swagger.json'}).then((res: any) => {
                                const ret = Object.keys(res.paths);
                                const data = [];
                                for (const item of ret) {
                                    const obj: any = {};
                                    obj.label = item;
                                    obj.value = item;
                                    data.push(obj);
                                }
                                return data;
                            });
                        },
                    }),
                    column: {
                        minWidth: 250,
                        sortable: true,
                    },
                    form: {
                        rules: [{required: true, message: '必填项'}],
                        component: {
                            props: {
                                allowCreate: true,
                                filterable: true,
                                clearable: true,
                            },
                        },
                        helper: {
                            render() {
                                return <el-alert title="请正确填写，以免请求时被拦截。匹配单例使用正则,例如:/api/xx/.*?/"
                                                 type="warning"/>;
                            },
                        },
                    },
                },
            },
        },
    };
};
