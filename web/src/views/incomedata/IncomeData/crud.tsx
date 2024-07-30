// IncomeData CRUD TypeScript - Auto-generated on 2024-07-22 11:26:56

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
        const datas = await api.GetList(query);
        for (const data of datas.data) {
            for (const key in data.data) {
                if (Array.isArray(data.data[key])) {
                    data.data[key] = data.data[key].length;
                }
            }
            data.data = JSON.stringify(data.data)

            if (data.error && data.error.info) {
                data['error_info'] = JSON.stringify(data.error.info);
                data['error'] = JSON.stringify(data.error, null, 4);
            }
        }
        console.log('datas', datas);
        return datas;
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
                        show: auth("IncomeData:Create")
                    }
                }
            },
            rowHandle: {
                fixed: 'right',
                align: 'center',
                width: 140,
                buttons: {
                    view: {show: false},
                    edit: {show: false},
                    remove: {show: false},
                    download: {
                        show: true,
                        text: '下载日志',
                        type: 'text',
                        icon: 'Download',
                        click: async ({row}: any) => {
                            const blob = new Blob([row.error], {type: 'text/plain'});
                            const url = window.URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.href = url;
                            a.download = row.date + '.txt';
                            a.click();
                            window.URL.revokeObjectURL(url);
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
                }, date: {
                    title: "日期",
                    type: "date",
                    search: {show: true, component: {props: {clearable: true}}},
                    column: {
                        width: 140,
                        sortable: true,
                    },
                    form: {
                        rules: [
                            {required: true, message: '请输入日期'},
                        ],
                        component: {
                            props: {
                                clearable: true,
                                format: "YYYY-MM-DD",
                                "value-format": "YYYY-MM-DD",
                            }
                        },
                    },
                }, data: {
                    title: "数据",
                    type: "text",
                    form: {show: false},
                    column: {
                        align: 'center',
                        showOverflowTooltip: true,
                    },
                }, error_info: {
                    title: "信息",
                    type: "text",
                    form: {show: false},
                    column: {
                        showOverflowTooltip: true,
                    }
                },
            },
        },
    };

}