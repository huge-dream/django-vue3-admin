import {dict} from "@fast-crud/fast-crud";
import {shallowRef} from 'vue'
import deptFormat from "/@/components/dept-format/index.vue";

export const commonCrudConfig = (options = {
    create_datetime: {
        form: false,
        table: false,
        search: false
    },
    update_datetime: {
        form: false,
        table: false,
        search: false
    },
    creator_name: {
        form: false,
        table: false,
        search: false
    },
    modifier_name: {
        form: false,
        table: false,
        search: false
    },
    dept_belong_id: {
        form: false,
        table: false,
        search: false
    },
    description: {
        form: false,
        table: false,
        search: false
    },
}) => {
    return {
        dept_belong_id: {
            title: '所属部门',
            type: 'dict-tree',
            search: {
                show: options.dept_belong_id?.search || false
            },
            dict: dict({
                url: '/api/system/dept/all_dept/',
                isTree: true,
                value: 'id',
                label: 'name',
                children: 'children',
            }),
            column: {
                align: 'center',
                width: 300,
                show: options.dept_belong_id?.table || false,
                component: {
                    name: shallowRef(deptFormat),
                    vModel: "modelValue",
                }
            },
            form: {
                show: options.dept_belong_id?.form || false,
                component: {
                    multiple: false,
                    clearable: true,
                    props: {
                        checkStrictly: true,
                        props: {
                            // 为什么这里要写两层props
                            // 因为props属性名与fs的动态渲染的props命名冲突，所以要多写一层
                            label: "name",
                            value: "id",
                        }
                    }
                },
                helper: "默认不填则为当前创建用户的部门ID"
            }
        },
        description: {
            title: '备注',
            search: {
                show: options.description?.search || false
            },
            type: 'textarea',
            column: {
                width: 100,
                show: options.description?.table || false,
            },
            form: {
                show: options.description?.form || false,
                component: {
                    placeholder: '请输入内容',
                    showWordLimit: true,
                    maxlength: '200',
                }
            },
            viewForm: {
                show: true
            }
        },
        modifier_name: {
            title: '修改人',
            search: {
                show: options.modifier_name?.search || false
            },
            column: {
                width: 100,
                show: options.modifier_name?.table || false,
            },
            form: {
                show: false,
            },
            viewForm: {
                show: true
            }
        },
        creator_name: {
            title: '创建人',
            search: {
                show: options.creator_name?.search || false
            },
            column: {
                width: 100,
                show: options.creator_name?.table || false,
            },
            form: {
                show: false,
            },
            viewForm: {
                show: true
            }
        },
        update_datetime: {
            title: '更新时间',
            type: 'datetime',
            search: {
                show: options.update_datetime?.search || false,
                col: {span: 8},
                component: {
                    type: 'datetimerange',
                    props: {
                        'start-placeholder': '开始时间',
                        'end-placeholder': '结束时间',
                        'value-format': 'YYYY-MM-DD HH:mm:ss',
                        'picker-options': {
                            shortcuts: [{
                                text: '最近一周',
                                onClick(picker) {
                                    const end = new Date();
                                    const start = new Date();
                                    start.setTime(start.getTime() - 3600 * 1000 * 24 * 7);
                                    picker.$emit('pick', [start, end]);
                                }
                            }, {
                                text: '最近一个月',
                                onClick(picker) {
                                    const end = new Date();
                                    const start = new Date();
                                    start.setTime(start.getTime() - 3600 * 1000 * 24 * 30);
                                    picker.$emit('pick', [start, end]);
                                }
                            }, {
                                text: '最近三个月',
                                onClick(picker) {
                                    const end = new Date();
                                    const start = new Date();
                                    start.setTime(start.getTime() - 3600 * 1000 * 24 * 90);
                                    picker.$emit('pick', [start, end]);
                                }
                            }]
                        }
                    }
                },
                valueResolve(context: any) {
                    const {key, value} = context
                    //value解析，就是把组件的值转化为后台所需要的值
                    //在form表单点击保存按钮后，提交到后台之前执行转化
                    if (value) {
                        context.form.update_datetime_after = value[0]
                        context.form.update_datetime_before = value[1]
                    }
                    //  ↑↑↑↑↑ 注意这里是form，不是row
                }
            },
            column: {
                width: 160,
                show: options.update_datetime?.table || false,
            },
            form: {
                show: false,
            },
            viewForm: {
                show: true
            }
        },
        create_datetime: {
            title: '创建时间',
            type: 'datetime',
            search: {
                show: options.create_datetime?.search || false,
                col: {span: 8},
                component: {
                    type: 'datetimerange',
                    props: {
                        'start-placeholder': '开始时间',
                        'end-placeholder': '结束时间',
                        'value-format': 'YYYY-MM-DD HH:mm:ss',
                        'picker-options': {
                            shortcuts: [{
                                text: '最近一周',
                                onClick(picker) {
                                    const end = new Date();
                                    const start = new Date();
                                    start.setTime(start.getTime() - 3600 * 1000 * 24 * 7);
                                    picker.$emit('pick', [start, end]);
                                }
                            }, {
                                text: '最近一个月',
                                onClick(picker) {
                                    const end = new Date();
                                    const start = new Date();
                                    start.setTime(start.getTime() - 3600 * 1000 * 24 * 30);
                                    picker.$emit('pick', [start, end]);
                                }
                            }, {
                                text: '最近三个月',
                                onClick(picker) {
                                    const end = new Date();
                                    const start = new Date();
                                    start.setTime(start.getTime() - 3600 * 1000 * 24 * 90);
                                    picker.$emit('pick', [start, end]);
                                }
                            }]
                        }
                    }
                },
                valueResolve(context: any) {
                    const {key, value} = context
                    //value解析，就是把组件的值转化为后台所需要的值
                    //在form表单点击保存按钮后，提交到后台之前执行转化
                    if (value) {
                        context.form.create_datetime_after = value[0]
                        context.form.create_datetime_before = value[1]
                    }
                    //  ↑↑↑↑↑ 注意这里是form，不是row
                }
            },
            column: {
                width: 160,
                show: options.create_datetime?.table || false,
            },
            form: {
                show: false
            },
            viewForm: {
                show: true
            }
        }
    }
}
