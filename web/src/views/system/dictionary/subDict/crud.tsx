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
import { useI18n } from 'vue-i18n';
import { dictionary } from '/@/utils/dictionary';

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
          title: t('message.pages.dictionary.subTable.columns.index'),
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
          title: t('message.pages.dictionary.subTable.columns.label'),
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
              { required: true, message: t('message.pages.dictionary.subTable.validation.labelRequired') },
            ],
            component: {
              props: {
                clearable: true,
              },
              placeholder: t('message.pages.dictionary.subTable.form.labelPlaceholder'),
            },
          },
        },
        type: {
          title: t('message.pages.dictionary.subTable.columns.type'),
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
              { label: t('message.pages.dictionary.subTable.typeLabels.text'), value: 0 },
              { label: t('message.pages.dictionary.subTable.typeLabels.number'), value: 1 },
              { label: t('message.pages.dictionary.subTable.typeLabels.date'), value: 2 },
              { label: t('message.pages.dictionary.subTable.typeLabels.datetime'), value: 3 },
              { label: t('message.pages.dictionary.subTable.typeLabels.time'), value: 4 },
              { label: t('message.pages.dictionary.subTable.typeLabels.file'), value: 5 },
              { label: t('message.pages.dictionary.subTable.typeLabels.boolean'), value: 6 },
              { label: t('message.pages.dictionary.subTable.typeLabels.images'), value: 7 },
            ],
          }),
          form: {
            rules: [
              // 表单校验规则
              { required: true, message: t('message.pages.dictionary.subTable.validation.typeRequired') },
            ],
            value: 0,
            component: {
              props: {
                clearable: true,
              },
              placeholder: t('message.pages.dictionary.subTable.form.typePlaceholder'),
            },
          },
        },
        value: {
          title: t('message.pages.dictionary.subTable.columns.value'),
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
          type: 'input',
          form: {
            rules: [
              // 表单校验规则
              { required: true, message: t('message.pages.dictionary.subTable.validation.valueRequired') },
            ],
            component: {
              props: {
                clearable: true,
              },
              placeholder: t('message.pages.dictionary.subTable.form.valuePlaceholder'),
            },
          },
        },
        status: {
          title: t('message.pages.dictionary.subTable.columns.status'),
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
              { required: true, message: t('message.pages.dictionary.subTable.validation.statusRequired') },
            ],
          },
        },
        sort: {
          title: t('message.pages.dictionary.subTable.columns.sort'),
          width: 70,
          type: 'number',
          form: {
            value: 1,
            component: {},
            rules: [
              // 表单校验规则
              { required: true, message: t('message.pages.dictionary.subTable.validation.sortRequired') },
            ],
          },
        },
        color: {
          title: t('message.pages.dictionary.subTable.columns.color'),
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
          title: t('message.pages.dictionary.subTable.columns.isValue'),
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
