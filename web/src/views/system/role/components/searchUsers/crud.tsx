import {getRoleUsersAuthorized, removeRoleUser} from './api';
import {
  compute,
  dict,
  UserPageQuery,
  AddReq,
  DelReq,
  EditReq,
  CrudOptions,
  CreateCrudOptionsProps,
  CreateCrudOptionsRet
} from '@fast-crud/fast-crud';

import {auth} from "/@/utils/authFunction";
import { ref , nextTick} from 'vue';
import XEUtils from 'xe-utils';

export const createCrudOptions = function ({ crudExpose, context }: CreateCrudOptionsProps): CreateCrudOptionsRet {
  const pageRequest = async (query: UserPageQuery) => {
    return await getRoleUsersAuthorized(query);
  };
  const editRequest = async ({ form, row }: EditReq) => {
    return undefined;
  };
  const delRequest = async ({ row }: DelReq) => {
    return await removeRoleUser(crudExpose.crudRef.value.getSearchFormData().role_id, [row.id]);
  };
  const addRequest = async ({ form }: AddReq) => {
    return undefined;
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
      request: {
        pageRequest,
        addRequest,
        editRequest,
        delRequest,
      },
      actionbar: {
        buttons: {
          add: {
            show: auth('role:AuthorizedAdd'),
            click: (ctx: any) => {
              context!.subUserRef.value.dialog = true;
							nextTick(() => {
								context!.subUserRef.value.setSearchFormData({ form: { role_id: crudExpose.crudRef.value.getSearchFormData().role_id } });
								context!.subUserRef.value.doRefresh();
							});
						},
          },
        },
        
      },
      rowHandle: {
        //固定右侧
        fixed: 'left',
        width: 120,
        show: auth('role:AuthorizedDel'),
        buttons: {
          view: {
            show: false,
          },
          edit: {
            show: false,
          },
          remove: {
            iconRight: 'Delete',
            show: true,
          },
        },
      },
      table: {
				rowKey: "id",
        onSelectionChange,
        onRefreshed: () => toggleRowSelection(),
			},
      columns: {
        $checked: {
					title: "选择",
					form: { show: false},
					column: {
						show: auth('role:AuthorizedDel'),
						type: "selection",
						align: "center",
						width: "55px",
						columnSetDisabled: true, //禁止在列设置中选择
					}
				  },
        _index: {
          title: '序号',
          form: { show: false },
          column: {
            //type: 'index',
            align: 'center',
            width: '70px',
            columnSetDisabled: true, //禁止在列设置中选择
            formatter: (context) => {
              //计算序号,你可以自定义计算规则，此处为翻页累加
              let index = context.index ?? 1;
              let pagination = crudExpose!.crudBinding.value.pagination;
              // @ts-ignore
              return ((pagination.currentPage ?? 1) - 1) * pagination.pageSize + index + 1;
            },
          },
        },
        name: {
          title: '用户名',
          search: {
            show: true,
            component: {
              props: {
                clearable: true,
              },
            },
          },
          type: 'text',
          form: {
            show: false,
          },
        },
        dept: {
          title: '部门',
          show: true,
          type: 'dict-tree',
          column: {
            name: 'text',
            formatter({value,row,index}){
                return row.dept__name
            }
          },
          search: {
            show: true,
            disabled: true,
            col:{span: 6},
            component: {
              multiple: false,
              props: {
                checkStrictly: true,
                clearable: true,
                filterable: true,
              },
            },
          },
          form: {
            show: false
          },
          dict: dict({
            isTree: true,
            url: '/api/system/dept/all_dept/',
            value: 'id',
            label: 'name'
          }),
        },
      },
    },
  };
};
