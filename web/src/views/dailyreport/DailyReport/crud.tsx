// DailyReport CRUD TypeScript - Auto-generated on 2024-07-08 15:06:12

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
import {commonCrudConfig} from "/@/utils/commonCrud";
// 注意：以下FastCrud配置应替换为实际的JavaScript/TypeScript代码片段
export const createCrudOptions = function ({crudExpose}: CreateCrudOptionsProps): CreateCrudOptionsRet {
    const pageRequest = async (query: UserPageQuery) => {
        const datas = await api.GetList(query);
        for (const data of datas.data) {
            for (const key of Object.keys(data.data)) {
                if (Array.isArray(data.data[key])) {
                    data.data[key] = `${data.data[key].length}条`;
                }
                if (key === 'instance') {
                    data.data['服务器状态条目'] = data.data[key];
                    delete data.data[key];
                } else if (key === 'income') {
                    data.data['收入参考数据'] = data.data[key];
                    delete data.data[key];
                } else if (key === 'banhao') {
                    data.data['版号参考收入数据'] = data.data[key];
                    delete data.data[key];
                }
            }
            data.data = JSON.stringify(data.data);

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
                        show: auth("reportdata:Create")
                    }
                }
            },
            rowHandle: {
                show: false,
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
                            },
                            events: {
                                change: (e: any) => {
                                    console.log(e);
                                }
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
                },
                ...commonCrudConfig()
            },
        },
    };

}