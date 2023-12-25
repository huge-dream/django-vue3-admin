import { dict } from "@fast-crud/fast-crud";
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
        description: {
            title: '备注',
            search: {
                show: options.description?.search || false
            },
            type: 'textarea',
            column: {
                show: options.description?.table || false,
            },
            form: {
                component: {
                    show: options.description?.form || false,
                    placeholder: '请输入内容',
                    showWordLimit: true,
                    maxlength: '200',
                }
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
            }
        },
        update_datetime: {
            title: '更新时间',
            type: 'datetime',
            search: {
                show: options.update_datetime?.search || false
            },
            column: {
                width: 160,
                show: options.update_datetime?.table || false,
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
            }
        },
        create_datetime: {
            title: '创建时间',
            type: 'datetime',
            search: {
                show: options.create_datetime?.search || false
            },
            column: {
                width: 160,
                show: options.create_datetime?.table || false,
            }
        },
        dept_belong_id: {
            title: '所属部门',
            type: 'dict-tree',
            search: {
                show:  false
            },
            dict: dict({
                url: '/api/system/dept/all_dept/',
                isTree: true,
                value: 'id',
                label: 'name',
                children: 'children' // 数据字典中children字段的属性名
            }),
            column: {
                width: 150,
                show: options.dept_belong_id?.table || false,
            },
            form: {
                component: {
                    show: options.dept_belong_id?.form || false,
                    multiple: false,
                    clearable: true,
                    props: {
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
        }
    }
}
