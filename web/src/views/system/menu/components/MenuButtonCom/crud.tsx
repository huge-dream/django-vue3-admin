import {AddReq, DelReq, EditReq, dict, CreateCrudOptionsRet, CreateCrudOptionsProps} from '@fast-crud/fast-crud';
import { useI18n } from 'vue-i18n';
import * as api from './api';
import {auth} from '/@/utils/authFunction'
import {request} from '/@/utils/service';
import { successNotification } from '/@/utils/message';
import { ElMessage } from 'element-plus';
import { nextTick, ref } from 'vue';
import XEUtils from 'xe-utils';
//此处为crudOptions配置
export const createCrudOptions = function ({crudExpose, context}: CreateCrudOptionsProps): CreateCrudOptionsRet {
	const { t } = useI18n()
    const pageRequest = async () => {
        if (context!.selectOptions.value.id) {
            return await api.GetList({menu: context!.selectOptions.value.id} as any);
        } else {
            return undefined;
        }
    };
    const editRequest = async ({form, row}: EditReq) => {
        return await api.UpdateObj({...form, menu: row.menu});
    };
    const delRequest = async ({row}: DelReq) => {
        return await api.DelObj(row.id);
    };
    const addRequest = async ({form}: AddReq) => {
        return await api.AddObj({...form, ...{menu: context!.selectOptions.value.id}});
    };
    // 记录选中的行
	const selectedRows = ref<any>([]);

	const onSelectionChange = (changed: any) => {
		const tableData = crudExpose.getTableData();
		const unChanged = tableData.filter((row: any) => !changed.includes(row));
		// 添加已选择的行
		XEUtils.arrayEach(changed, (item: any) => {
			const ids = XEUtils.pluck(selectedRows.value, 'id');
			if (!ids.includes(item.id)) {
				selectedRows.value = XEUtils.union(selectedRows.value, [item]);
			}
		});
		// 剔除未选择的行
		XEUtils.arrayEach(unChanged, (unItem: any) => {
			selectedRows.value = XEUtils.remove(selectedRows.value, (item: any) => item.id !== unItem.id);
		});
	};
	const toggleRowSelection = () => {
		// 多选后，回显默认勾选
		const tableRef = crudExpose.getBaseTableRef();
		const tableData = crudExpose.getTableData();
		const selected = XEUtils.filter(tableData, (item: any) => {
			const ids = XEUtils.pluck(selectedRows.value, 'id');
			return ids.includes(item.id);
		});

		nextTick(() => {
			XEUtils.arrayEach(selected, (item) => {
				tableRef.toggleRowSelection(item, true);
			});
		});
	};
    
    return {
        selectedRows,
        crudOptions: {
            pagination:{
                show:false
            },
            search: {
                container: {
                    action: {
                        //按钮栏配置
                        col: {
                            span: 8,
                        },
                    },
                },
            },
            actionbar: {
                buttons: {
                    add: {
                        show: auth('menu:CreateButton')
                    },
                    batchAdd: {
						show: true,
						type: 'primary',
						text: t('message.pages.menu.validation.batchGenerate'),
						click: async () => {
							if (context!.selectOptions.value.id == undefined) {
								ElMessage.error(t('message.pages.menu.messages.selectMenu'));
								return;
							}
							const result = await api.BatchAdd({ menu: context!.selectOptions.value.id });
							if (result.code == 2000) {
								successNotification(result.msg);
								crudExpose.doRefresh();
							}
						},
					},
                },
            },
            rowHandle: {
                //固定右侧
                fixed: 'right',
                width: 200,
                buttons: {
                    view: {
                        show: false,
                    },
                    edit: {
                        iconRight: 'Edit',
                        type: 'text',
                        show: auth('menu:UpdateButton')
                    },
                    remove: {
                        iconRight: 'Delete',
                        type: 'text',
                        show: auth('menu:DeleteButton')
                    },
                },
            },
            request: {
                pageRequest,
                addRequest,
                editRequest,
                delRequest,
            },
            table: {
				rowKey: 'id', //设置你的主键id， 默认rowKey=id
				onSelectionChange,
				onRefreshed: () => toggleRowSelection(),
			},
            form: {
                col: {span: 24},
                labelWidth: '100px',
                wrapper: {
                    is: 'el-dialog',
                    width: '600px',
                },
            },
            columns: {
                $checked: {
					title: t('message.pages.menu.buttons.select'),
					form: { show: false },
					column: {
						type: 'selection',
						align: 'center',
						width: '70px',
						columnSetDisabled: true, //禁止在列设置中选择
					},
				},
                _index: {
                    title: t('message.pages.menu.buttons.index'),
                    form: {show: false},
                    column: {
                        type: 'index',
                        align: 'center',
                        width: '70px',
                        columnSetDisabled: true, //禁止在列设置中选择
                    },
                },
                search: {
                    title: t('message.pages.menu.buttons.search'),
                    column: {show: false},
                    type: 'text',
                    search: {show: true},
                    form: {
                        show: false,
                        component: {
                            placeholder: t('message.pages.menu.buttons.searchPlaceholder'),
                        },
                    },
                },
                id: {
                    title: 'ID',
                    type: 'text',
                    column: {show: false},
                    search: {show: false},
                    form: {show: false},
                },
                name: {
                    title: t('message.pages.menu.buttons.permissionName'),
                    type: 'text',
                    search: {show: true},
                    column: {
                        minWidth: 120,
                        sortable: true,
                    },
                    form: {
                        rules: [{required: true, message: t('message.pages.menu.validation.permissionNameRequired')}],
                        component: {
                            placeholder: t('message.pages.menu.buttons.searchPlaceholder'),
                            props: {
                                clearable: true,
                                allowCreate: true,
                                filterable: true,
                            },
                        },
                    },
                },
                value: {
                    title: t('message.pages.menu.buttons.permissionValue'),
                    type: 'text',
                    search: {show: false},
                    column: {
                        width: 200,
                        sortable: true,
                    },
                    form: {
                        rules: [{required: true, message: t('message.pages.menu.validation.permissionValueRequired')}],
                        placeholder: t('message.pages.menu.buttons.apiEndpoint'),
                    },
                },
                method: {
                    title: t('message.pages.menu.buttons.requestMethod'),
                    search: {show: false},
                    type: 'dict-select',
                    column: {
                        width: 120,
                        sortable: true,
                    },
                    dict: dict({
                        data: [
                            {label: 'GET', value: 0},
                            {label: 'POST', value: 1, color: 'success'},
                            {label: 'PUT', value: 2, color: 'warning'},
                            {label: 'DELETE', value: 3, color: 'danger'},
                        ],
                    }),
                    form: {
                        rules: [{required: true, message: t('message.pages.menu.validation.methodRequired')}],
                    },
                },
                api: {
                    title: t('message.pages.menu.buttons.apiEndpoint'),
                    search: {show: false},
                    type: 'dict-select',
                    dict: dict({
                        getData() {
                            return request({url: '/swagger.json'}).then((res: any) => {
                                const ret = Object.keys(res.paths);
                                const data = [];
                                for (const item of ret) {
                                    const obj: any = {};
                                    obj.label = item;
                                    obj.value = item;
                                    data.push(obj);
                                }
                                return data;
                            });
                        },
                    }),
                    column: {
                        minWidth: 250,
                        sortable: true,
                    },
                    form: {
                        rules: [{required: true, message: t('message.pages.menu.validation.apiRequired')}],
                        component: {
                            props: {
                                allowCreate: true,
                                filterable: true,
                                clearable: true,
                            },
                        },
                    },
                },
            },
        },
    };
};
