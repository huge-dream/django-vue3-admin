// AuthorizationLetter CRUD TypeScript - Auto-generated on 2024-07-15 16:30:40

import * as api from './api';
import {
    AddReq,
    CreateCrudOptionsProps,
    CreateCrudOptionsRet,
    DelReq,
    dict,
    EditReq,
    UserPageQuery
} from '@fast-crud/fast-crud';
import {dictionary} from '/@/utils/dictionary';
import {auth} from '/@/utils/authFunction'
import {commonCrudConfig} from "/@/utils/commonCrud";
import {errorMessage, infoMessage, successMessage} from "/@/utils/message";
import {computed} from "vue";
// 注意：以下FastCrud配置应替换为实际的JavaScript/TypeScript代码片段
export const createCrudOptions = function ({crudExpose}: CreateCrudOptionsProps): CreateCrudOptionsRet {
    const pageRequest = async (query: UserPageQuery) => {
        const lists = await api.GetList(query);
        lists.data.forEach((item: any) => {
            if (item.authorization_filepath
                && item.authorization_filepath.startsWith("/home/BuildAuthorization/Output/")
                && item.authorization_filepath.endsWith(".zip")) {

                // 去掉前缀部分
                let new_filepath = String(item.authorization_filepath.replace("/home/BuildAuthorization/Output/", ""));

                // 创建新的对象格式
                item.authorization_filepath = {
                    id: item.id,
                    label: new_filepath,
                };
            }
        });
        return lists;
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
                        show: auth("AuthorizationLetter:Create")
                    },
                    clear: {
                        show: auth("AuthorizationLetter:Clear"),
                        text: '清理文件',
                        type: 'info',
                        click: async () => {
                            const result = await api.ClearAuthorizationLetter();
                            if (result.status) {
                                successMessage(`${result.message}`);
                            } else {
                                errorMessage(`${result.message}`);
                            }
                            crudExpose?.doRefresh();
                        }
                    }
                }
            },
            rowHandle: {
                //固定右侧
                fixed: 'right',
                align: 'center',
                // width: 240,
                width: 200,
                buttons: {
                    view: {
                        show: false,
                    },
                    edit: {
                        show: auth("AuthorizationLetter:Update"),
                        type: 'text',
                        iconRight: 'Edit',
                    },
                    remove: {
                        show: auth("AuthorizationLetter:Delete"),
                        type: 'text',
                        iconRight: 'Delete',
                    },
                    generate: {
                        title: '生成',
                        text: '生成',
                        type: 'text',
                        iconRight: 'Upload',
                        show: auth("AuthorizationLetter:Generate"),
                        click: async (obj) => {
                            const result = await api.GenerateAuthorizationLetter(obj.row.id);
                            if (result.status) {
                                successMessage(`${result.message}`);
                            } else {
                                errorMessage(`${result.message}`);
                            }
                            crudExpose?.doRefresh();
                        }
                    },
                    download: {
                        title: '下载',
                        text: '下载',
                        type: 'text',
                        iconRight: 'Download',
                        // show: auth("AuthorizationLetter:Download"),
                        show:  computed(() => {
                            return false;
                        }),
                        click: async (obj) => {
                            const response = await api.DownloadAuthorizationLetter(obj.row.id);
                            try {
                                if (response.data) {
                                    if (response.headers['content-type'] === 'application/json') {
                                        const reader = new FileReader();
                                        reader.readAsText(response.data);
                                        reader.onload = function (e) {
                                            const res = JSON.parse(reader.result as string);
                                            errorMessage(`下载失败: ${res.message}`);
                                        }
                                    } else {
                                        const blob = new Blob([response.data], {type: response.headers['content-type']});
                                        const url = window.URL.createObjectURL(blob);
                                        const a = document.createElement('a');
                                        a.style.display = 'none';
                                        a.href = url;
                                        a.download = `${obj.row.name}授权书.zip`;  // 动态设置文件名
                                        document.body.appendChild(a);
                                        a.click();
                                        window.URL.revokeObjectURL(url);
                                        successMessage(`开始下载: ${obj.row.name}授权书.zip`);
                                    }
                                } else {
                                    errorMessage(`下载失败: ${response.message}`);
                                }
                            } catch (e) {
                                errorMessage(`调用失败: ${e}`);

                            }
                        }
                    }
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
                }, name: {
                    title: "游戏名称",
                    type: "input",
                    column: {
                        align: 'center',
                        sortable: true,
                        width: '250',
                    },
                    form: {
                        rules: [
                            {required: true, message: '请输入游戏名称', trigger: 'blur'}
                        ]
                    },
                    search: {
                        show: true,
                        component: {
                            props: {
                                clearable: true,
                            },
                        },
                    }
                }, release_date: {
                    title: "发行日期",
                    type: "date",
                    column: {
                        align: 'center',
                        sortable: true,
                        format: "YYYY-MM-DD",
                        "value-format": "YYYY-MM-DD",
                    },
                    form: {
                        rules: [
                            {required: true, message: '请选择发行日期', trigger: 'blur'}
                        ],
                        component: {
                            props: {
                                clearable: true,
                                format: "YYYY-MM-DD",
                                "value-format": "YYYY-MM-DD",
                            },
                        },
                    }

                }, authorization_filepath: {
                    title: "授权书文件路径",
                    type: "dict-select",
                    column: {
                        showOverflowTooltip: true,
                        align: 'center',
                        component: {
                            color: 'primary',
                            onClick: async (row: any) => {
                                const response = await api.DownloadAuthorizationLetter(row.item.id);
                            try {
                                if (response.data) {
                                    if (response.headers['content-type'] === 'application/json') {
                                        const reader = new FileReader();
                                        reader.readAsText(response.data);
                                        reader.onload = function (e) {
                                            const res = JSON.parse(reader.result as string);
                                            errorMessage(`下载失败: ${res.message}`);
                                        }
                                    } else if (response.headers['content-type'] === 'application/zip') {
                                        const blob = new Blob([response.data], {type: response.headers['content-type']});
                                        const url = window.URL.createObjectURL(blob);
                                        const a = document.createElement('a');
                                        a.style.display = 'none';
                                        a.href = url;
                                        a.download = String(`${row.item.label}`.split('/').pop());
                                        document.body.appendChild(a);
                                        a.click();
                                        window.URL.revokeObjectURL(url);
                                        successMessage(`开始下载: ${row.item.label}`);
                                    }
                                } else {
                                    errorMessage(`下载失败: ${response.message}`);
                                }
                            } catch (e) {
                                errorMessage(`调用失败: ${e}`);

                            }
                            }
                        }
                    },
                    form: {
                        show: false
                    },
                }, tips: {
                    title: "备注",
                    type: "input",
                    column: {
                        align: 'center',
                        show: false,
                    },
                    form: {
                        show: false
                    }

                }, status: {
                    title: "授权书文件状态",
                    type: "dict-select",
                    column: {
                        width: '150',
                        align: 'center',
                    },
                    form: {
                        show: false
                    },
                    dict: dict({
                        data: dictionary('authorizationletter_status'),
                        value: 'value',
                        label: 'label',
                    }),
                    search: {
                        show: true,
                        component: {
                            props: {
                                clearable: true,
                            },
                        },
                    }

                },
                ...commonCrudConfig(
                    {
                        create_datetime: {
                            table: true,
                            search: true,
                        }
                    }
                )
            },
        },
    };

}