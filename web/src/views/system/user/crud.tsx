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
import { request } from '/@/utils/service';
import { dictionary } from '/@/utils/dictionary';
import { successMessage } from '/@/utils/message';
import { auth } from '/@/utils/authFunction';
import { SystemConfigStore } from "/@/stores/systemConfig";
import { storeToRefs } from "pinia";
import { computed } from "vue";
import { Md5 } from 'ts-md5';
import { commonCrudConfig } from "/@/utils/commonCrud";
import { ElMessageBox } from 'element-plus';
import { exportData } from "./api";
import { useI18n } from 'vue-i18n';

export const createCrudOptions = function ({ crudExpose }: CreateCrudOptionsProps): CreateCrudOptionsRet {
    const { t } = useI18n()
    const pageRequest = async (query: UserPageQuery) => {
        return await api.GetList(query);
    };
    const editRequest = async ({ form, row }: EditReq) => {
        form.id = row.id;
        return await api.UpdateObj(form);
    };
    const delRequest = async ({ row }: DelReq) => {
        return await api.DelObj(row.id);
    };
    const addRequest = async ({ form }: AddReq) => {
        return await api.AddObj(form);
    };

    const exportRequest = async (query: UserPageQuery) => {
        return await api.exportData(query)
    }

    const resetToDefaultPasswordRequest = async (row: EditReq) => {
        await api.resetToDefaultPassword(row.id)
        successMessage("重置密码成功")
    }

    const systemConfigStore = SystemConfigStore()
    const { systemConfig } = storeToRefs(systemConfigStore)
    const getSystemConfig = computed(() => {
        // console.log(systemConfig.value)
        return systemConfig.value
    })


    return {
        crudOptions: {
            table: {
                remove: {
                    confirmMessage: t('message.pages.user.dialog.deleteConfirm'),
                },
            },
            request: {
                pageRequest,
                addRequest,
                editRequest,
                delRequest,
            },
            form: {
                initialForm: {
                    password: computed(() => {
                        return systemConfig.value['base.default_password']
                    }),
                }
            },
            actionbar: {
                buttons: {
                    add: {
                        show: auth('user:Create')
                    },
                    export: {
                        text: t('message.pages.user.buttons.export'),//按钮文字
                        title: t('message.pages.user.buttons.export'),//鼠标停留显示的信息
                        show: auth('user:Export'),
                        click: (ctx: any) => ElMessageBox.confirm(
    t('message.pages.user.dialog.exportConfirm'), t('message.pages.user.dialog.exportTitle'),
                            { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
                        ).then(() => exportData(ctx.row))
                    }
                }
            },
            rowHandle: {
                //固定右侧
                fixed: 'right',
                width: 220,
                buttons: {
                    view: {
                        show: false,
                    },
                    edit: {
                        iconRight: 'Edit',
                        type: 'text',
                        show: auth('user:Update'),
                    },
                    remove: {
                        iconRight: 'Delete',
                        type: 'text',
                        show: auth('user:Delete'),
                    },
                    resetDefaultPwd: {
                        text: t('message.pages.user.buttons.resetPassword'),
                        type: 'text',
                        iconRight: 'Setting',
                        show: auth('user:ResetDefaultPassword'),
                        click: (ctx: any) => ElMessageBox.confirm(
                            t('message.pages.user.dialog.resetPasswordConfirm'), t('message.pages.user.dialog.resetPassword'),
                            { confirmButtonText: t('message.pages.user.buttons.confirm'), cancelButtonText: t('message.pages.user.buttons.cancel'), type: 'warning' }
                        ).then(() => resetToDefaultPasswordRequest(ctx.row))
                    },
                },
            },
            columns: {
                _index: {
                    title: t('message.pages.user.table.columns.index'),
                    form: { show: false },
                    column: {
                        type: 'index',
                        align: 'center',
                        width: '70px',
                        columnSetDisabled: true, //禁止在列设置中选择
                    },
                },
                username: {
                    title: t('message.pages.user.table.columns.username'),
                    search: {
                        show: true,
                    },
                    type: 'input',
                    column: {
                        minWidth: 100, //最小列宽
                    },
                    form: {
                        rules: [
                            // 表单校验规则
                            {
                                required: true,
                                message: t('message.pages.user.validation.usernameRequired'),
                            },
                        ],
                        component: {
                            placeholder: t('message.pages.user.form.usernamePlaceholder'),
                        },
                    },
                },
                password: {
                    title: '密码',
                    type: 'password',
                    column: {
                        show: false,
                    },
                    editForm: {
                        show: false,
                    },
                    form: {
                        rules: [
                            // 表单校验规则
                            {
                                required: true,
                                message: t('message.pages.user.validation.passwordRequired'),
                            },
                        ],
                        component: {

                            span: 12,
                            showPassword: true,
                            placeholder: t('message.pages.user.form.passwordPlaceholder'),
                        },
                    },
                    valueResolve({ form }) {
                        if (form.password) {
                            form.password = Md5.hashStr(form.password)
                        }
                    }
                },
                name: {
                    title: t('message.pages.user.table.columns.name'),
                    search: {
                        show: true,
                    },
                    type: 'input',
                    column: {
                        minWidth: 100, //最小列宽
                    },
                    form: {
                        rules: [
                            // 表单校验规则
                            {
                                required: true,
                                message: t('message.pages.user.validation.nameRequired'),
                            },
                        ],
                        component: {
                            span: 12,
                            placeholder: t('message.pages.user.form.namePlaceholder'),
                        },
                    },
                },
                dept: {
                    title: t('message.pages.user.table.columns.dept'),
                    type: 'dict-tree',
                    dict: dict({
                        isTree: true,
                        url: '/api/system/dept/all_dept/',
                        value: 'id',
                        label: 'name'
                    }),
                    column: {
                        minWidth: 300, //最小列宽
                        formatter({ value, row, index }) {
                            return row.dept_name_all
                        }
                    },
                    form: {
                        rules: [
                            // 表单校验规则
                            {
                                required: true,
                                message: t('message.pages.user.validation.deptRequired'),
                            },
                        ],
                        component: {
                            filterable: true,
                            placeholder: t('message.pages.user.form.deptPlaceholder'),
                            props: {
                                checkStrictly: true,
                                props: {
                                    value: 'id',
                                    label: 'name',
                                },
                            },
                        },
                    },
                },
                manage_dept: {
                    title: t('message.pages.user.table.columns.manageDept'),
                    type: 'dict-tree',
                    dict: dict({
                        isTree: true,
                        url: '/api/system/dept/all_dept/',
                        value: 'id',
                        label: 'name'
                    }),
                    column: {
                        minWidth: 300
                    },
                    form: {
                        value: [],
                        component: {
                            filterable: true,
                            multiple: true,
                            placeholder: t('message.pages.user.form.deptPlaceholder'),
                            clearable: true,
                            collapseTags: true,
                            maxCollapseTags: 2,
                            collapseTagsTooltip: true,
                            props: {
                                checkStrictly: true,
                                props: {
                                    value: 'id',
                                    label: 'name',
                                },
                            },
                        },
                        helper: t('message.pages.user.validation.manageDeptHelper'),
                    },
                },
                role: {
                    title: t('message.pages.user.table.columns.role'),
                    search: {
                        disabled: true,
                    },
                    type: 'dict-select',
                    dict: dict({
                        url: '/api/system/role/',
                        value: 'id',
                        label: 'name',
                    }),
                    column: {
                        minWidth: 200, //最小列宽
                        // formatter({ value, row, index }) {
                        //     const values = row.role_info.map((item: any) => item.name);
                        //     return values.join(',')
                        // }
                    },
                    form: {
                        rules: [
                            // 表单校验规则
                            {
                                required: true,
                                message: t('message.pages.user.validation.deptRequired'),
                            },
                        ],
                        component: {
                            multiple: true,
                            filterable: true,
                            placeholder: t('message.pages.user.form.rolePlaceholder'),
                        },
                    },
                },
                mobile: {
                    title: t('message.pages.user.table.columns.mobile'),
                    search: {
                        show: true,
                    },
                    type: 'input',
                    column: {
                        minWidth: 120, //最小列宽
                    },
                    form: {
                        rules: [
                            {
                                max: 20,
                                message: t('message.pages.user.validation.mobileInvalid'),
                                trigger: 'blur',
                            },
                            {
                                pattern: /^1[3-9]\d{9}$/,
                                message: t('message.pages.user.validation.mobileInvalid'),
                            },
                        ],
                        component: {
                            placeholder: t('message.pages.user.form.mobilePlaceholder'),
                        },
                    },
                },
                email: {
                    title: t('message.pages.user.table.columns.email'),
                    column: {
                        width: 260,
                    },
                    form: {
                        rules: [
                            {
                                type: 'email',
                                message: t('message.pages.user.validation.emailInvalid'),
                                trigger: ['blur', 'change'],
                            },
                        ],
                        component: {
                            placeholder: t('message.pages.user.form.emailPlaceholder'),
                        },
                    },
                },
                gender: {
                    title: t('message.pages.user.table.columns.gender'),
                    type: 'dict-select',
                    dict: dict({
                        data: dictionary('gender'),
                    }),
                    form: {
                        value: 1,
                        component: {
                            span: 12,
                        },
                    },
                    component: { props: { color: 'auto' } }, // 自动染色
                },
                user_type: {
                    title: t('message.pages.user.table.columns.userType'),
                    search: {
                        show: true,
                    },
                    type: 'dict-select',
                    dict: dict({
                        data: dictionary('user_type'),
                    }),
                    column: {
                        minWidth: 100, //最小列宽
                    },
                    form: {
                        show: false,
                        value: 0,
                        component: {
                            span: 12,
                        },
                    },
                },
                is_active: {
                    title: t('message.pages.user.table.columns.status'),
                    search: {
                        show: true,
                    },
                    type: 'dict-radio',
                    column: {
                        component: {
                            name: 'fs-dict-switch',
                            activeText: '',
                            inactiveText: '',
                            style: '--el-switch-on-color: var(--el-color-primary); --el-switch-off-color: #dcdfe6',
                            onChange: compute((context) => {
                                return () => {
                                    api.UpdateObj(context.row).then((res: APIResponseData) => {
                                        successMessage(res.msg as string);
                                    });
                                };
                            }),
                        },
                    },
                    dict: dict({
                        data: dictionary('button_status_bool'),
                    }),
                    form: {
                        value: true
                    }
                },
                avatar: {
                    title: t('message.pages.user.table.columns.avatar'),
                    type: 'avatar-uploader',
                    align: 'center',
                    form: {
                        show: false,
                    },
                    column: {
                        minWidth: 100, //最小列宽
                    },
                },
                ...commonCrudConfig({
                    dept_belong_id: {
                        form: false,
                        table: false
                    }
                })
            },
        },
    };
};
