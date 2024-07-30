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
import {errorMessage, successMessage} from '/@/utils/message';
import {auth} from '/@/utils/authFunction'
import {ElMessage, ElMessageBox} from "element-plus";
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
            rowHandle: {
                fixed: 'right',
                align: 'center',
                width: 100,
                buttons: {
                    view: {
                        show: true,
                        type: 'text',
                    },
                    edit: {
                        show: false,
                    },
                    remove: {
                        show: false,
                    },
                    renew: {
                        title: '续费',
                        text: '续费',
                        iconRight: '',
                        type: 'text',
                        show: auth('consoles:Renew'),
                        click: async (obj) => {
                            // 弹出确认框
                            ElMessageBox.confirm(
                                '是否确认续费？',
                                '确认续费',
                                {
                                    confirmButtonText: '确认',
                                    cancelButtonText: '取消',
                                    type: 'warning',
                                }
                            ).then(async () => {
                                // 在请求开始时弹出提示框
                                const loadingMessage = ElMessage({
                                    message: '正在续费，请稍候...（至少3s）',
                                    type: 'info',
                                    showClose: false,
                                    duration: 0, // 持续显示，直到手动关闭
                                });
                                try {
                                    const result = await api.RenewObj(obj.row);
                                    console.log(result);
                                    if (result.status) {
                                        successMessage(`${result.message}: ${JSON.stringify(result.data)}`);
                                        crudExpose?.doRefresh();
                                    } else {
                                        errorMessage(`${result.message}: ${result.data}`);
                                    }
                                } catch (e) {
                                    errorMessage(`续费失败: ${e}`);
                                }
                                loadingMessage.close();
                            }).catch(() => {
                                // 用户取消了操作
                                errorMessage('续费操作已取消');
                            });
                        }

                    }
                }
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
                }, account: {
                    title: "账号",
                    type: "text",
                    column: {
                        width: 100,
                    }

                }, instance_id: {
                    title: "实例Id",
                    type: "text",
                    column: {
                        showOverflowTooltip: true,
                    }

                }, instance_name: {
                    title: "实例名称",
                    type: "text",
                    column: {
                        showOverflowTooltip: true,
                    }

                }, status: {
                    title: "状态",
                    type: "text",
                    column: {
                        width: 100,
                    }

                }, instance_type_id: {
                    title: "规格",
                    type: "text",
                    column: {
                        width: 150,
                    }

                }, cpus: {
                    title: "Cpu",
                    type: "text",
                    column: {
                        width: 100,
                    }

                }, memory_size: {
                    title: "内存",
                    type: "text",
                    column: {
                        width: 100,
                    }

                }, eip_address: {
                    title: "主Ipv4地址",
                    type: "text",
                    column: {
                        width: 150,
                    }

                }, instance_charge_type: {
                    title: "实例计费类型",
                    type: "text",
                    column: {
                        width: 120,
                    }

                }, expired_at: {
                    title: "到期时间",
                    type: "datetime",
                    column: {
                        width: 160,
                        align: 'center',
                    }

                },
            },
        },
    };

}