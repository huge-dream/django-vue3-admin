export interface PageQuery {
  page: number;
  limit: number;
}

export interface APIResponseData {
  code?: number;
  data: any;
  msg?: string;
}

export interface CurrentInfoType {
  role: string;
  model: string;
  app: string;

  menu: string;
}

export interface ModelItemType {
  app: string;
  key: string;
  title: string;
  showText?: string;
}

export interface AddColumnsDataType extends CurrentInfoType {
  id?: number | string;
  field_name: string;
  title: string;
  is_query: boolean;
  is_create: boolean;
  is_update: boolean;
}

export interface ColumnsFormDataType {
  id?: number | string;
  field_name: string;
  title: string;
  is_create: boolean;
  is_update: boolean;
  is_query: boolean;
}
