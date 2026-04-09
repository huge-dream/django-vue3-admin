import { dict, CreateCrudOptionsProps, CreateCrudOptionsRet } from '@fast-crud/fast-crud'
import * as api from './api'
import { GetCompanies } from '../currency/api'
import { GetList as GetCurrencies } from '../currency/api'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'

export const createCrudOptions = function ({ crudExpose }: Partial<CreateCrudOptionsProps>): CreateCrudOptionsRet {
  void crudExpose
  const { t } = useI18n()

  const loadCompanyOptions = async () => {
    try {
      const res = await GetCompanies({ page: 1, page_size: 1000, pageSize: 1000 })
      const list =
        res?.data?.data?.results ||
        res?.data?.results ||
        res?.data?.list ||
        res?.data ||
        res?.results ||
        res?.list ||
        []
      return (Array.isArray(list) ? list : []).map((c: any) => ({
        company_code: c.company_code,
        company_short_name: c.company_short_name || c.company_code || c.company_name
      }))
    } catch (e) {
      console.warn('Failed to load company list', e)
      return []
    }
  }

  const loadCurrencyOptions = async (companyCode?: string) => {
    try {
      const params: any = { page: 1, page_size: 500, pageSize: 500 }
      if (companyCode) params.factory = companyCode
      const res = await GetCurrencies(params)
      const list =
        res?.data?.data?.results ||
        res?.data?.results ||
        res?.data?.list ||
        res?.data ||
        res?.results ||
        res?.list ||
        []
      return (Array.isArray(list) ? list : []).map((c: any) => ({
        value: c.currencycode || c.currency_code,
        label: c.currencyname || c.currency_code || c.currencycode || c.currency_name
      }))
    } catch (e) {
      console.warn('Failed to load currency list', e)
      return []
    }
  }

  const ensureSupplierUnique = async (companyCode: string, supplierId: string, currentId?: number) => {
    if (!companyCode || !supplierId) return
    const res = await api.GetList({ company_code: companyCode, supplier_id: supplierId, page: 1, page_size: 1, pageSize: 1 })
    const list =
      res?.data?.data?.results ||
      res?.data?.results ||
      res?.data?.list ||
      res?.data ||
      res?.results ||
      res?.list ||
      []
    const exists = Array.isArray(list)
      ? list.find((item: any) => item.company_code === companyCode && item.supplier_id === supplierId)
      : null
    if (exists && (!currentId || exists.id !== currentId)) {
      throw new Error(t('message.pages.basicinfo.supplier.supplierId') + t('message.pages.menu.validation.alreadyExists'))
    }
  }

  // Pre-load company options
  void loadCompanyOptions()

  return {
    crudOptions: {
      form: {
        labelWidth: '110px'
      },
      request: {
        pageRequest: async (query) => api.GetList(query),
        addRequest: async ({ form }) => {
          try {
            await ensureSupplierUnique(form.company_code, form.supplier_id)
            return await api.AddObj(form)
          } catch (err: any) {
            ElMessage.error(err?.message || '保存失败')
            throw err
          }
        },
        editRequest: async ({ form, row }) => {
          try {
            await ensureSupplierUnique(form.company_code, form.supplier_id, row.id)
            return await api.UpdateObj({ ...form, id: row.id })
          } catch (err: any) {
            ElMessage.error(err?.message || '保存失败')
            throw err
          }
        },
        delRequest: async ({ row }) => api.DelObj(row.id)
      },
      table: {
        rowKey: 'id'
      },
      actionbar: {
        buttons: {
          add: { show: true }
        }
      },
      rowHandle: {
        fixed: 'right'
      },
      columns: {
        company_code: {
          title: t('message.pages.basicinfo.supplier.companyCode'),
          type: 'dict-select',
          dict: dict({
            cache: false,
            value: 'company_code',
            label: 'company_short_name',
            getData: async () => loadCompanyOptions()
          }),
          search: { show: true },
          form: {
            rules: [{ required: true, message: t('message.pages.basicinfo.supplier.companyCode') + ' ' + t('message.pages.menu.validation.fieldNameRequired') }],
            component: {
              on: {
                change({ form, value }: any) {
                  form.transaction_currency = undefined
                  form.company_code = value
                }
              }
            }
          },
          column: { minWidth: 160, showOverflowTooltip: true }
        },
        supplier_id: {
          title: t('message.pages.basicinfo.supplier.supplierId'),
          type: 'input',
          search: { show: true, component: { props: { placeholder: t('message.pages.basicinfo.supplier.supplierId'), clearable: true } } },
          form: { rules: [{ required: true, message: t('message.pages.basicinfo.supplier.supplierId') + ' ' + t('message.pages.menu.validation.fieldNameRequired') }] },
          column: { minWidth: 140, showOverflowTooltip: true }
        },
        supplier_name: {
          title: t('message.pages.basicinfo.supplier.supplierName'),
          type: 'input',
          search: { show: true, component: { props: { placeholder: t('message.pages.basicinfo.supplier.supplierName'), clearable: true } } },
          form: { rules: [{ required: true, message: t('message.pages.basicinfo.supplier.supplierName') + ' ' + t('message.pages.menu.validation.fieldNameRequired') }] },
          column: { minWidth: 180, showOverflowTooltip: true }
        },
        supplier_short_name: {
          title: t('message.pages.basicinfo.supplier.supplierShortName'),
          type: 'input',
          form: { rules: [{ required: true, message: t('message.pages.basicinfo.supplier.supplierShortName') + ' ' + t('message.pages.menu.validation.fieldNameRequired') }] },
          column: { minWidth: 160, showOverflowTooltip: true }
        },
        vendor_type: {
          title: t('message.pages.basicinfo.supplier.vendorType'),
          type: 'dict-select',
          dict: dict({ data: [
            { value: '国有', label: t('message.pages.pissupplier.vendorType.stateOwned') },
            { value: '集体', label: t('message.pages.pissupplier.vendorType.collective') },
            { value: '私营', label: t('message.pages.pissupplier.vendorType.private') },
            { value: '合资', label: t('message.pages.pissupplier.vendorType.joint') },
            { value: '独资', label: t('message.pages.pissupplier.vendorType.whollyOwned') },
            { value: '其他', label: t('message.pages.pissupplier.vendorType.other') },
          ] }),
          column: { minWidth: 140, showOverflowTooltip: true }
        },
        payment_terms: {
          title: t('message.pages.basicinfo.supplier.paymentTerms'),
          type: 'dict-select',
          dict: dict({ data: [
            { value: 'tt_30_70', label: t('message.pages.pissupplier.paymentTerms.tt30_70') },
            { value: 'net30', label: t('message.pages.pissupplier.paymentTerms.net30') },
            { value: 'net45', label: t('message.pages.pissupplier.paymentTerms.net45') },
            { value: 'prepaid', label: t('message.pages.pissupplier.paymentTerms.prepaid') },
          ] }),
          column: { minWidth: 160, showOverflowTooltip: true }
        },
        transaction_currency: {
          title: t('message.pages.basicinfo.supplier.transactionCurrency'),
          type: 'dict-select',
          dict: dict({
            cache: false,
            getData: async ({ form }: any = {}) => {
              return loadCurrencyOptions(form?.company_code)
            }
          }),
          form: { placeholder: '先选择交易厂区' },
          column: { minWidth: 140, showOverflowTooltip: true }
        },
        incoterms: {
          title: t('message.pages.basicinfo.supplier.incoterms'),
          type: 'dict-select',
          dict: dict({ data: [
            { value: 'EXW', label: 'EXW' },
            { value: 'FCA', label: 'FCA' },
            { value: 'CPT', label: 'CPT' },
            { value: 'CIP', label: 'CIP' },
            { value: 'DAP', label: 'DAP' },
            { value: 'DPU', label: 'DPU' },
            { value: 'DDP', label: 'DDP' },
            { value: 'FAS', label: 'FAS' },
            { value: 'FOB', label: 'FOB' },
            { value: 'CFR', label: 'CFR' },
            { value: 'CIF', label: 'CIF' },
          ] }),
          column: { minWidth: 160, showOverflowTooltip: true }
        },
        supplier_level: {
          title: t('message.pages.basicinfo.supplier.supplierLevel'),
          type: 'input',
          column: { minWidth: 120, showOverflowTooltip: true }
        },
        contact_person: {
          title: t('message.pages.basicinfo.supplier.contactPerson'),
          type: 'input',
          form: { rules: [{ required: true, message: t('message.pages.basicinfo.supplier.contactPerson') + ' ' + t('message.pages.menu.validation.fieldNameRequired') }] },
          column: { minWidth: 120, showOverflowTooltip: true }
        },
        contact_phone: {
          title: t('message.pages.basicinfo.supplier.contactPhone'),
          type: 'input',
          form: { rules: [{ required: true, message: t('message.pages.basicinfo.supplier.contactPhone') + ' ' + t('message.pages.menu.validation.fieldNameRequired') }] },
          column: { minWidth: 140, showOverflowTooltip: true }
        },
        contact_email: {
          title: t('message.pages.basicinfo.supplier.contactEmail'),
          type: 'input',
          form: { rules: [{ required: true, message: t('message.pages.basicinfo.supplier.contactEmail') + ' ' + t('message.pages.menu.validation.fieldNameRequired') }] },
          column: { minWidth: 180, showOverflowTooltip: true }
        },
        country: {
          title: t('message.pages.basicinfo.supplier.country'),
          type: 'input',
          form: { rules: [{ required: true, message: t('message.pages.basicinfo.supplier.country') + ' ' + t('message.pages.menu.validation.fieldNameRequired') }] },
          column: { minWidth: 120, showOverflowTooltip: true }
        },
        province: {
          title: t('message.pages.basicinfo.supplier.province'),
          type: 'input',
          form: { rules: [{ required: true, message: t('message.pages.basicinfo.supplier.province') + ' ' + t('message.pages.menu.validation.fieldNameRequired') }] },
          column: { minWidth: 120, showOverflowTooltip: true }
        },
        city: {
          title: t('message.pages.basicinfo.supplier.city'),
          type: 'input',
          column: { minWidth: 120, showOverflowTooltip: true }
        },
        address: {
          title: t('message.pages.basicinfo.supplier.address'),
          type: 'textarea',
          column: { minWidth: 200, showOverflowTooltip: true },
          form: { component: { props: { rows: 2 } } }
        },
        postal_code: {
          title: t('message.pages.basicinfo.supplier.postalCode'),
          type: 'input',
          column: { minWidth: 120, showOverflowTooltip: true }
        },
        status: {
          title: t('message.pages.basicinfo.supplier.status'),
          type: 'dict-switch',
          dict: dict({ data: [{ value: 1, label: t('message.pages.basicinfo.supplier.enabled') }, { value: 0, label: t('message.pages.basicinfo.supplier.disabled') }] }),
          form: { value: 1 },
          column: { width: 120 }
        },
        create_datetime: {
          title: t('message.pages.basicinfo.supplier.createTime'),
          type: 'datetime',
          form: { show: false },
          column: { width: 180 }
        },
        update_datetime: {
          title: t('message.pages.basicinfo.supplier.updateTime'),
          type: 'datetime',
          form: { show: false },
          column: { width: 180 }
        }
      }
    }
  }
}
