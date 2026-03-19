import { request } from '/@/utils/service';

export type PriceTemplatePayload = {
  name: string;
  procurement_category: 'strategic' | 'misc';
  category: 'tooling' | 'stamping' | 'injection';
  remark?: string;
  active: boolean;
  enable_cost_structure: boolean;
  sections: any[];
};

const baseUrl = '/api/procurement/price_template/';

export const fetchPriceTemplates = (params?: Record<string, unknown>) =>
  request({
    url: baseUrl,
    method: 'get',
    params,
  });

export const fetchPriceTemplateDetail = (id: string | number) =>
  request({
    url: `${baseUrl}${id}/`,
    method: 'get',
  });

export const createPriceTemplate = (data: PriceTemplatePayload) =>
  request({
    url: baseUrl,
    method: 'post',
    data,
  });

export const updatePriceTemplate = (id: string | number, data: PriceTemplatePayload) =>
  request({
    url: `${baseUrl}${id}/`,
    method: 'put',
    data,
  });

export const deletePriceTemplate = (id: string | number) =>
  request({
    url: `${baseUrl}${id}/`,
    method: 'delete',
  });
