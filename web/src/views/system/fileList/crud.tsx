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
import { useI18n } from 'vue-i18n';
import fileSelector from '/@/components/fileSelector/index.vue';
import { getBaseURL } from '/@/utils/baseUrl';

export const createCrudOptions = function ({ crudExpose, context }: CreateCrudOptionsProps): CreateCrudOptionsRet {
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
        defaultOption: {
          show: false,
          label: t('message.pages.fileList.tabs.all')
        },
        options: [
          { value: 0, label: t('message.pages.fileList.tabs.image') },
          { value: 1, label: t('message.pages.fileList.tabs.video') },
          { value: 2, label: t('message.pages.fileList.tabs.audio') },
          { value: 3, label: t('message.pages.fileList.tabs.other') },
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
          title: t('message.pages.fileList.table.columns.index'),
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
          title: t('message.pages.fileList.table.columns.keyword'),
          column: {
            show: false,
          },
          search: {
            show: true,
            component: {
              props: {
                clearable: true,
              },
              placeholder: t('message.pages.fileList.form.keywordPlaceholder'),
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
          title: t('message.pages.fileList.table.columns.name'),
          search: {
            show: true,
          },
          type: 'input',
          column: {
            minWidth: 200,
          },
          form: {
            component: {
              placeholder: t('message.pages.fileList.form.namePlaceholder'),
              clearable: true
            },
          },
        },
        preview: {
          title: t('message.pages.fileList.table.columns.preview'),
          column: {
            minWidth: 120,
            align: 'center'
          },
          form: {
            show: false
          }
        },
        url: {
          title: t('message.pages.fileList.table.columns.url'),
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
          title: t('message.pages.fileList.table.columns.md5sum'),
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
          title: t('message.pages.fileList.table.columns.mimeType'),
          type: 'input',
          form: {
            show: false,
          },
          column: {
            minWidth: 160
          }
        },
        file_type: {
          title: t('message.pages.fileList.table.columns.fileType'),
          type: 'dict-select',
          dict: dict({
            data: [
              { label: t('message.pages.fileList.fileType.image'), value: 0, color: 'success' },
              { label: t('message.pages.fileList.fileType.video'), value: 1, color: 'warning' },
              { label: t('message.pages.fileList.fileType.audio'), value: 2, color: 'danger' },
              { label: t('message.pages.fileList.fileType.other'), value: 3, color: 'primary' },
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
              placeholder: t('message.pages.fileList.form.fileTypePlaceholder')
            }
          }
        },
        size: {
          title: t('message.pages.fileList.table.columns.size'),
          column: {
            minWidth: 120
          },
          form: {
            show: false
          }
        },
        upload_method: {
          title: t('message.pages.fileList.table.columns.uploadMethod'),
          type: 'dict-select',
          dict: dict({
            data: [
              { label: t('message.pages.fileList.uploadMethod.default'), value: 0, color: 'primary' },
              { label: t('message.pages.fileList.uploadMethod.selector'), value: 1, color: 'warning' },
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
          title: t('message.pages.fileList.table.columns.createTime'),
          column: {
            minWidth: 160
          },
          form: {
            show: false
          }
        },
      },
    },
  };
};
