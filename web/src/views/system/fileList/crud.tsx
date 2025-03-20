import * as api from './api';
import {
  UserPageQuery,
  AddReq,
  DelReq,
  EditReq,
  CrudExpose,
  CrudOptions,
  CreateCrudOptionsProps,
  CreateCrudOptionsRet,
  dict
} from '@fast-crud/fast-crud';
import fileSelector from '/@/components/fileSelector/index.vue';
import { getBaseURL } from '/@/utils/baseUrl';

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
    return await api.AddObj(form);
  };
  return {
    crudOptions: {
      actionbar: {
        buttons: {
          add: {
            show: true,
            click: () => context.openAddHandle?.()
          },
        },
      },
      request: {
        pageRequest,
        addRequest,
        editRequest,
        delRequest,
      },
      tabs: {
        show: true,
        name: 'file_type',
        type: '',
        options: [
          { value: 0, label: '图片' },
          { value: 1, label: '视频' },
          { value: 2, label: '音频' },
          { value: 3, label: '其他' },
        ]
      },
      rowHandle: {
        //固定右侧
        fixed: 'right',
        width: 200,
        show: false,
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
        name: {
          title: '文件名称',
          search: {
            show: true,
          },
          type: 'input',
          column: {
            minWidth: 200,
          },
          form: {
            component: {
              placeholder: '请输入文件名称',
              clearable: true
            },
          },
        },
        preview: {
          title: '预览',
          column: {
            minWidth: 120,
            align: 'center'
          },
          form: {
            show: false
          }
        },
        url: {
          title: '文件地址',
          type: 'file-uploader',
          search: {
            disabled: true,
          },
          column: {
            minWidth: 360,
            component: {
                async buildUrl(value: any) {
                    return getBaseURL(value);
                    }
            }
          },
        },
        md5sum: {
          title: '文件MD5',
          search: {
            disabled: true,
          },
          column: {
            minWidth: 300,
          },
          form: {
            disabled: false
          },
        },
        mime_type: {
          title: '文件类型',
          type: 'input',
          form: {
            show: false,
          },
          column: {
            minWidth: 160
          }
        },
        file_type: {
          title: '文件类型',
          type: 'dict-select',
          dict: dict({
            data: [
              { label: '图片', value: 0, color: 'success' },
              { label: '视频', value: 1, color: 'warning' },
              { label: '音频', value: 2, color: 'danger' },
              { label: '其他', value: 3, color: 'primary' },
            ]
          }),
          column: {
            show: false
          },
          search: {
            show: true
          },
          form: {
            show: false,
            component: {
              placeholder: '请选择文件类型'
            }
          }
        },
        size: {
          title: '文件大小',
          column: {
            minWidth: 120
          },
          form: {
            show: false
          }
        },
        upload_method: {
          title: '上传方式',
          type: 'dict-select',
          dict: dict({
            data: [
              { label: '默认上传', value: 0, color: 'primary' },
              { label: '文件选择器上传', value: 1, color: 'warning' },
            ]
          }),
          column: {
            minWidth: 140
          },
          search: {
            show: true
          }
        },
        create_datetime: {
          title: '创建时间',
          column: {
            minWidth: 160
          },
          form: {
            show: false
          }
        },
        // fileselectortest: {
        //   title: '文件选择器测试',
        //   type: 'file-selector',
        //   column: {
        //     minWidth: 200
        //   },
        //   form: {
        //     component: {
        //       name: fileSelector,
        //       vModel: 'modelValue',
        //       tabsShow: 0b1111,
        //       itemSize: 100,
        //       multiple: true,
        //       selectable: true,
        //       showInput: true,
        //       inputType: 'image',
        //       valueKey: 'url',
        //     }
        //   }
        // }
      },
    },
  };
};
