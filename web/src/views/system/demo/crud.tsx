import * as api from './api';
import {
    UserPageQuery,
    AddReq,
    DelReq,
    EditReq,
    CreateCrudOptionsProps,
    CreateCrudOptionsRet,
    dict
} from '@fast-crud/fast-crud';
import {commonCrudConfig} from "/@/utils/commonCrud";
import {computed,shallowRef} from "vue";
import dvaSelect from "/@/components/dvaSelect/index.vue";
export const createCrudOptions = function ({
                                               crudExpose,
                                               isEcharts,
                                               initChart
                                           }: CreateCrudOptionsProps): CreateCrudOptionsRet {
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
                        show: true,
                    },
                    showEcharts: {
                        type: 'warning',
                        text: computed(() => {
                            return isEcharts.value ? '隐藏图表' : '显示图表'
                        }),
                        click: () => {
                            isEcharts.value = !isEcharts.value;
                        }
                    }
                },
            },
            rowHandle: {
                fixed: 'right',
                width: 100,
                buttons: {
                    view: {
                        type: 'text',
                    },
                    edit: {
                        show: false,
                    },
                    remove: {
                        show: false,
                    },
                },
            },
            columns: {
                _index: {
                    title: '序号',
                    form: {show: false},
                    column: {
                        //type: 'index',
                        align: 'center',
                        width: '70px',
                        columnSetDisabled: true, //禁止在列设置中选择
                        formatter: (context) => {
                            //计算序号,你可以自定义计算规则，此处为翻页累加
                            let index = context.index ?? 1;
                            let pagination = crudExpose!.crudBinding.value.pagination;
                            return ((pagination!.currentPage ?? 1) - 1) * pagination!.pageSize + index + 1;
                        },
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
                username: {
                    title: '测试自定义组件',
                    dict:dict({
                        url({form}){
                            return  '/api/system/role/'
                        },
                        label:'name',
                        value:'id'
                        }),
                    form: {
                        component: {
                            //局部引用子表格，要用shallowRef包裹
                            name: shallowRef(dvaSelect),
                        }
                    }
                },
                // username: {
                //     title: '登录用户名',
                //     search: {
                //         disabled: false,
                //     },
                //     type: 'input',
                //     column: {
                //         minWidth: 120,
                //     },
                //     form: {
                //         disabled: true,
                //         component: {
                //             placeholder: '请输入登录用户名',
                //         },
                //     },
                // },
                ip: {
                    title: '登录ip',
                    search: {
                        disabled: false,
                    },
                    type: 'input',
                    column: {
                        minWidth: 120,
                    },
                    form: {
                        disabled: true,
                        component: {
                            placeholder: '请输入登录ip',
                        },
                    },
                },
                isp: {
                    title: '运营商',
                    search: {
                        disabled: true,
                    },
                    disabled: true,
                    type: 'input',
                    column: {
                        minWidth: 120,
                    },
                    form: {
                        component: {
                            placeholder: '请输入运营商',
                        },
                    },
                },
                continent: {
                    title: '大州',
                    type: 'input',
                    column: {
                        minWidth: 90,
                    },
                    form: {
                        disabled: true,
                        component: {
                            placeholder: '请输入大州',
                        },
                    },
                    component: {props: {color: 'auto'}}, // 自动染色
                },
                country: {
                    title: '国家',
                    type: 'input',
                    column: {
                        minWidth: 90,
                    },
                    form: {
                        component: {
                            placeholder: '请输入国家',
                        },
                    },
                    component: {props: {color: 'auto'}}, // 自动染色
                },
                province: {
                    title: '省份',
                    type: 'input',
                    column: {
                        minWidth: 80,
                    },
                    form: {
                        component: {
                            placeholder: '请输入省份',
                        },
                    },
                    component: {props: {color: 'auto'}}, // 自动染色
                },
                city: {
                    title: '城市',
                    type: 'input',
                    column: {
                        minWidth: 80,
                    },
                    form: {
                        component: {
                            placeholder: '请输入城市',
                        },
                    },
                    component: {props: {color: 'auto'}}, // 自动染色
                },
                district: {
                    title: '县区',
                    key: '',
                    type: 'input',
                    column: {
                        minWidth: 80,
                    },
                    form: {
                        component: {
                            placeholder: '请输入县区',
                        },
                    },
                    component: {props: {color: 'auto'}}, // 自动染色
                },
                area_code: {
                    title: '区域代码',
                    type: 'input',
                    column: {
                        minWidth: 90,
                    },
                    form: {
                        component: {
                            placeholder: '请输入区域代码',
                        },
                    },
                    component: {props: {color: 'auto'}}, // 自动染色
                },
                country_english: {
                    title: '英文全称',
                    type: 'input',
                    column: {
                        minWidth: 120,
                    },
                    form: {
                        component: {
                            placeholder: '请输入英文全称',
                        },
                    },
                    component: {props: {color: 'auto'}}, // 自动染色
                },
                country_code: {
                    title: '简称',
                    type: 'input',
                    column: {
                        minWidth: 100,
                    },
                    form: {
                        component: {
                            placeholder: '请输入简称',
                        },
                    },
                    component: {props: {color: 'auto'}}, // 自动染色
                },
                longitude: {
                    title: '经度',
                    type: 'input',
                    disabled: true,
                    column: {
                        minWidth: 100,
                    },
                    form: {
                        component: {
                            placeholder: '请输入经度',
                        },
                    },
                    component: {props: {color: 'auto'}}, // 自动染色
                },
                latitude: {
                    title: '纬度',
                    type: 'input',
                    disabled: true,
                    column: {
                        minWidth: 100,
                    },
                    form: {
                        component: {
                            placeholder: '请输入纬度',
                        },
                    },
                    component: {props: {color: 'auto'}}, // 自动染色
                },
                login_type: {
                    title: '登录类型',
                    type: 'dict-select',
                    search: {
                        disabled: false,
                    },
                    dict: dict({
                        data: [
                            {label: '普通登录', value: 1},
                            {label: '微信扫码登录', value: 2},
                        ],
                    }),
                    column: {
                        minWidth: 120,
                    },
                    form: {
                        component: {
                            placeholder: '请选择登录类型',
                        },
                    },
                },
                os: {
                    title: '操作系统',
                    type: 'input',
                    column: {
                        minWidth: 120,
                    },
                    form: {
                        component: {
                            placeholder: '请输入操作系统',
                        },
                    },
                },
                browser: {
                    title: '浏览器名',
                    type: 'input',
                    column: {
                        minWidth: 120,
                    },
                    form: {
                        component: {
                            placeholder: '请输入浏览器名',
                        },
                    },
                },
                agent: {
                    title: 'agent信息',
                    disabled: true,
                    type: 'input',
                    column: {
                        minWidth: 120,
                    },
                    form: {
                        component: {
                            placeholder: '请输入agent信息',
                        },
                    },
                },
                ...commonCrudConfig({
                    create_datetime: {
                        search: true
                    }
                })
            },
        },
    };
};
