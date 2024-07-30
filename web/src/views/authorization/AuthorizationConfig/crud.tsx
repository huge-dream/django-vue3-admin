// AuthorizationConfig CRUD TypeScript - Auto-generated on 2024-07-15 10:36:58

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
                        show: auth("AuthorizationConfig:Create")
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
                        show: auth("AuthorizationConfig:Update")
                    },
                    remove: {
                        iconRight: 'Delete',
                        type: 'text',
                        show: auth("AuthorizationConfig:Delete")
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
                }, key: {
                    title: "配置键",
                    search: {
                        show: true,
                        component: {
                            props: {
                                clearable: true,
                            },
                        },
                    },
                    type: 'input',
                    form: {
                        rules: [
                            // 表单校验规则
                            {required: true, message: '名称必填项'},
                        ],
                        component: {
                            props: {
                                clearable: true,
                            },
                            placeholder: '请输入名称',
                        },
                    },
                }, value: {
                    title: "配置值",
                    type: 'input',
                    search: {
                        show: true,
                        component: {
                            props: {
                                clearable: true,
                            },
                        },
                    },
                    view: {
                        component: {props: {height: 100, width: 100}},
                    },
                    form: {
                        rules: [
                            // 表单校验规则
                            {required: true, message: '数据值必填项'},
                        ],
                        component: {
                            props: {
                                clearable: true,
                            },
                            placeholder: '请输入数据值',
                        },
                    },

                }, type: {
                    title: '数据值类型',
                    type: 'dict-select',
                    search: {
                        disabled: true,
                        component: {
                            props: {
                                clearable: true,
                            },
                        },
                    },
                    show: false,
                    dict: dict({
                        data: [
                            {label: 'text', value: 0},
                            {label: 'number', value: 1},
                            {label: 'date', value: 2},
                            {label: 'datetime', value: 3},
                            {label: 'time', value: 4},
                            {label: 'file', value: 5},
                            {label: 'boolean', value: 6},
                            {label: 'images', value: 7},
                        ],
                    }),
                    form: {
                        rules: [
                            // 表单校验规则
                            {required: true, message: '数据值类型必填项'},
                        ],
                        value: 0,
                        component: {
                            props: {
                                clearable: true,
                            },
                            placeholder: '请选择数据值类型',
                        },
                        /* valueChange(key, value, form, { getColumn, mode, component, immediate, getComponent }) {
                            const template = vm.getEditFormTemplate('value')
                            // 选择框重新选择后，情况value值
                            if (!immediate) {
                                form.value = undefined
                            }
                            if (value === 0) {
                                template.component.name = 'el-input'
                            } else if (value === 1) {
                                template.component.name = 'el-input-number'
                            } else if (value === 2) {
                                template.component.name = 'el-date-picker'
                                template.component.props = {
                                    type: 'date',
                                    valueFormat: 'yyyy-MM-dd'
                                }
                            } else if (value === 3) {
                                template.component.name = 'el-date-picker'
                                template.component.props = {
                                    type: 'datetime',
                                    valueFormat: 'yyyy-MM-dd HH:mm:ss'
                                }
                            } else if (value === 4) {
                                template.component.name = 'el-time-picker'
                                template.component.props = {
                                    pickerOptions: {
                                        arrowControl: true
                                    },
                                    valueFormat: 'HH:mm:ss'
                                }
                            } else if (value === 5) {
                                template.component.name = 'd2p-file-uploader'
                                template.component.props = { elProps: { listType: 'text' } }
                            } else if (value === 6) {
                                template.component.name = 'dict-switch'
                                template.component.value = true
                                template.component.props = {
                                    dict: {
                                        data: [
                                            { label: '是', value: 'true' },
                                            { label: '否', value: 'false' }
                                        ]
                                    }
                                }
                            } else if (value === 7) {
                                template.component.name = 'd2p-cropper-uploader'
                                template.component.props = { accept: '.png,.jpeg,.jpg,.ico,.bmp,.gif', cropper: { viewMode: 1 } }
                            }
                        }, */
                    },
                },
            },
        },
    };

}