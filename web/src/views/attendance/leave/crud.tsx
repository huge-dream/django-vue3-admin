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
import {successMessage, errorMessage} from '/@/utils/message';
import {auth} from '/@/utils/authFunction';
import {getRawSourceItemGetter} from "echarts/types/src/data/helper/dataProvider";
import {commonCrudConfig} from "/@/utils/commonCrud";
import {computed} from "vue";
// 注意：以下FastCrud配置应替换为实际的JavaScript/TypeScript代码片段

const calculateLeaveDuration = async (start_time: string, end_time: string) => {
    return await api.CalculateLeaveDuration({start_time, end_time});
};

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

    // noinspection TypeScriptValidateTypes
    return {
        crudOptions: {
            request: {
                pageRequest,
                addRequest,
                editRequest,
                delRequest
            },
            actionbar: {
                buttons: {
                    add: {
                        show: auth('leave:Create')
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
                        show: false,
                    },
                    edit: {
                        iconRight: 'Edit',
                        type: 'text',
                        show: auth("leave:Update")
                    },
                    remove: {
                        iconRight: 'Delete',
                        type: 'text',
                        show: auth("leave:Delete")
                    },
                    approval: {
                        title: '通过',
                        text: '通过',
                        iconRight: 'Check',
                        type: 'text',
                        show: auth("leave:Approval"),
                        click: async (obj) => {
                            const result = await api.approvalObj(obj.row, true);
                            if (result.status === true) {
                                successMessage(`审批状态已更新为通过: 状态 ${result.message}`);
                            } else {
                                errorMessage(`审批状态更新失败: ${result.message} ${result.data || ''}`);
                            }
                            crudExpose?.doRefresh();
                        }
                    },
                    reject: {
                        title: '驳回',
                        text: '驳回',
                        iconRight: 'Close',
                        type: 'text',
                        show: auth("leave:Approval"),
                        click: async (obj) => {
                            const result = await api.approvalObj(obj.row, false);
                            if (result.status === true) {
                                successMessage(`审批状态已更新为驳回: 状态 ${result.message}`);
                            } else {
                                errorMessage(`审批状态更新失败: ${result.message} ${result.data || ''}`);
                            }
                            crudExpose?.doRefresh();
                        }
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
                },
                creator_jobid: {
                    title: '工号',
                    type: 'input',
                    form: {
                        show: false,
                    },
                    column: {
                        show: auth("leave:Approval"),
                        minWidth: 120,
                        align: 'center',
                    },
                },
                creator: {
                    title: '创建者',
                    type: 'dict-select',
                    form: {
                        show: false,
                    },
                    column: {
                        show: false,
                    },
                    search: {
                        show: true,
                        component: {
                            props: {
                                clearable: true,
                                filterable: true,
                            },
                        },
                    },
                    dict: dict({
                        url: '/api/system/user/',
                        value: 'id',
                        label: 'name',
                    }),
                },
                creator_name: {},
                create_datetime: {},
                leave_type: {
                    title: "请假类型",
                    type: "dict-select",
                    dict: dict({
                        data: dictionary('leave_type'),
                        label: "label",
                        value: "value"
                    }),
                    column: {
                        align: 'center',
                        width: 100,
                    },
                    form: {
                        rules: [{required: true, message: '请选择请假类型'}],
                        component: {
                            props: {
                                clearable: true,
                            },
                        }
                    }, search: {
                        show: true,
                        component: {
                            props: {
                                clearable: true,
                            },
                        },
                    }
                }, start_time: {
                    title: "请假开始时间",
                    type: "datetime",
                    column: {
                        align: 'center',
                        width: 180,
                    },
                    form: {
                        rules: [{required: true, message: '请选择请假开始时间'}],
                        component: {
                            props: {
                                clearable: true,
                            },
                            events: {
                                change: async ({form}) => {
                                    if (form.start_time && form.end_time) {
                                        console.log(form.start_time)
                                        const result = await calculateLeaveDuration(form.start_time, form.end_time);
                                        form.duration = result.data;
                                        form.reference_duration = result.data;
                                    }
                                }
                            }
                        }
                    }
                }, end_time: {
                    title: "请假结束时间",
                    type: "datetime",
                    column: {
                        align: 'center',
                        width: 180,
                    },
                    form: {
                        rules: [{required: true, message: '请选择请假结束时间'}],
                        component: {
                            props: {
                                clearable: true,
                            },
                            events: {
                                change: async ({form}) => {
                                    if (form.start_time && form.end_time) {

                                        const result = await calculateLeaveDuration(form.start_time, form.end_time);
                                        console.log(result)
                                        form.duration = result.data;
                                        form.reference_duration = result.data;
                                    }
                                }
                            }
                        }
                    }
                }, duration: {
                    title: "请假时长",
                    type: 'text',
                    form: {
                        rules: [{required: true, message: '自动生成，按需进行手动修正'}],
                        component: {
                            props: {
                                clearable: true,
                            },
                        }
                    },
                    column: {
                        align: 'center',
                        width: 100,
                    },
                }, reference_duration: {
                    title: "参考时长",
                    type: 'text',
                    form: {
                        component: {
                            props: {
                                disabled: true,
                            },
                        }
                    },
                    column: {
                        align: 'center',
                        width: 100,
                    },
                }, reason: {
                    title: "请假原因",
                    type: "textarea",
                    showOverflowTooltip: true,
                    form: {
                        rules: [{required: true, message: '请输入请假原因'}],
                        component: {
                            props: {
                                clearable: true,
                            },
                        }
                    },
                    column: {
                        align: 'center',
                        width: 200,
                        showOverflowTooltip: true,
                    },
                }, status: {
                    title: "审批状态",
                    type: "dict-select",
                    dict: dict({
                        data: dictionary('approval_status'),
                        label: "label",
                        value: "value"
                    }),
                    form: {
                        show: false
                    },
                    column: {
                        align: 'center',
                        width: 100,
                    },
                    search: {
                        show: true,
                        component: {
                            props: {
                                clearable: true,
                            },
                        },
                    }
                },
                ...commonCrudConfig({
                        create_datetime: {
                            table: true,
                            search: true,
                        },
                        creator_name: {
                            table: true,
                        }
                    }
                )
            },
        },
    };

}