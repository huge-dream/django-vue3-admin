import * as api from './api';
import {
  dict,
  UserPageQuery,
  AddReq,
  DelReq,
  EditReq,
  CrudOptions,
  CreateCrudOptionsProps,
  CreateCrudOptionsRet
} from '@fast-crud/fast-crud';
import { dictionary } from '/@/utils/dictionary';

export const createCrudOptions = function ({ crudExpose, context }: CreateCrudOptionsProps): CreateCrudOptionsRet {
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
    const data = crudExpose!.getSearchFormData()
    const parent = data.parent
    form.parent = parent
    if (parent) {
      return await api.AddObj(form);
    } else {
      return undefined
    }

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
          },
          remove: {
            iconRight: 'Delete',
            type: 'text',
          },
        },
      },
      columns: {
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
        label: {
          title: '名称',
          search: {
            show: true,
            component: {
              props: {
                clearable: true,
              },
            },
          },
          type: 'input',
          form: {
            rules: [
              // 表单校验规则
              { required: true, message: '名称必填项' },
            ],
            component: {
              props: {
                clearable: true,
              },
              placeholder: '请输入名称',
            },
          },
        },
        type: {
          title: '数据值类型',
          type: 'dict-select',
          search: {
            disabled: true,
            component: {
              props: {
                clearable: true,
              },
            },
          },
          show: false,
          dict: dict({
            data: [
              { label: 'text', value: 0 },
              { label: 'number', value: 1 },
              { label: 'date', value: 2 },
              { label: 'datetime', value: 3 },
              { label: 'time', value: 4 },
              { label: 'file', value: 5 },
              { label: 'boolean', value: 6 },
              { label: 'images', value: 7 },
            ],
          }),
          form: {
            rules: [
              // 表单校验规则
              { required: true, message: '数据值类型必填项' },
            ],
            value: 0,
            component: {
              props: {
                clearable: true,
              },
              placeholder: '请选择数据值类型',
            },
            /* valueChange(key, value, form, { getColumn, mode, component, immediate, getComponent }) {
                const template = vm.getEditFormTemplate('value')
                // 选择框重新选择后，情况value值
                if (!immediate) {
                    form.value = undefined
                }
                if (value === 0) {
                    template.component.name = 'el-input'
                } else if (value === 1) {
                    template.component.name = 'el-input-number'
                } else if (value === 2) {
                    template.component.name = 'el-date-picker'
                    template.component.props = {
                        type: 'date',
                        valueFormat: 'yyyy-MM-dd'
                    }
                } else if (value === 3) {
                    template.component.name = 'el-date-picker'
                    template.component.props = {
                        type: 'datetime',
                        valueFormat: 'yyyy-MM-dd HH:mm:ss'
                    }
                } else if (value === 4) {
                    template.component.name = 'el-time-picker'
                    template.component.props = {
                        pickerOptions: {
                            arrowControl: true
                        },
                        valueFormat: 'HH:mm:ss'
                    }
                } else if (value === 5) {
                    template.component.name = 'd2p-file-uploader'
                    template.component.props = { elProps: { listType: 'text' } }
                } else if (value === 6) {
                    template.component.name = 'dict-switch'
                    template.component.value = true
                    template.component.props = {
                        dict: {
                            data: [
                                { label: '是', value: 'true' },
                                { label: '否', value: 'false' }
                            ]
                        }
                    }
                } else if (value === 7) {
                    template.component.name = 'd2p-cropper-uploader'
                    template.component.props = { accept: '.png,.jpeg,.jpg,.ico,.bmp,.gif', cropper: { viewMode: 1 } }
                }
            }, */
          },
        },
        value: {
          title: '数据值',
          search: {
            show: true,
            component: {
              props: {
                clearable: true,
              },
            },
          },
          view: {
            component: { props: { height: 100, width: 100 } },
          },
          /* // 提交时,处理数据
          valueResolve(row: any, col: any) {
              const value = row[col.key]
              const type = row.type
              if (type === 5 || type === 7) {
                  if (value != null) {
                      if (value.length >= 0) {
                          if (value instanceof Array) {
                              row[col.key] = value.toString()
                          } else {
                              row[col.key] = value
                          }
                      } else {
                          row[col.key] = null
                      }
                  }
              } else {
                  row[col.key] = value
              }
          },
          // 接收时,处理数据
          valueBuilder(row: any, col: any) {
              const value = row[col.key]
              const type = row.type
              if (type === 5 || type === 7) {
                  if (value != null && value) {
                      row[col.key] = value.split(',')
                  }
              } else {
                  row[col.key] = value
              }
          }, */
          type: 'input',
          form: {
            rules: [
              // 表单校验规则
              { required: true, message: '数据值必填项' },
            ],
            component: {
              props: {
                clearable: true,
              },
              placeholder: '请输入数据值',
            },
          },
        },
        status: {
          title: '状态',
          width: 80,
          search: {
            show: true
          },
          type: 'dict-radio',
          dict: dict({
            data: dictionary('button_status_bool'),
          }),
          form: {
            value: true,
            rules: [
              // 表单校验规则
              { required: true, message: '状态必填项' },
            ],
          },
        },
        sort: {
          title: '排序',
          width: 70,
          type: 'number',
          form: {
            value: 1,
            component: {},
            rules: [
              // 表单校验规则
              { required: true, message: '排序必填项' },
            ],
          },
        },
        color: {
          title: '标签颜色',
          width: 90,
          search: {
            disabled: true,
          },
          type: 'dict-select',
          dict: dict({
            data: [
              { label: 'success', value: 'success', color: 'success' },
              { label: 'primary', value: 'primary', color: 'primary' },
              { label: 'info', value: 'info', color: 'info' },
              { label: 'danger', value: 'danger', color: 'danger' },
              { label: 'warning', value: 'warning', color: 'warning' },
            ],
          }),
          form: {
            component: {
              props: {
                clearable: true,
              },
            },
          },
        },
        is_value: {
          title: '是否值',
          column: {
            show: false
          },
          form: {
            show: false,
            value: true
          }
        }
      },
    },
  };
};
