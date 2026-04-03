export interface TreeTypes {
  id?: number;
  name?: string;
  status?: boolean;
  children?: TreeTypes[];
}

export interface APIResponseData {
  code?: number;
  data: [];
  msg?: string;
}

export interface FormTypes<T> {
  [key: string]: T;
}

export interface ComponentFileItem {
  value: string;
  label: string;
}

export interface MenuTreeItemType {
  id: number | string;
  modifier_name: string;
  creator_name: string;
  create_datetime: string;
  update_datetime: string;
  menuPermission: string[];
  hasChild: boolean;
  description: string;
  modifier: string;
  dept_belong_id: string;
  icon: string;
  name: string;
  sort: number;
  is_link: boolean;
  is_catalog: boolean;
  web_path: string;
  component: string;
  component_name: string;
  status: boolean;
  cache: boolean;
  visible: boolean;
  creator: string;
  parent: number | string;
  is_iframe:boolean;
  is_affix:boolean;
  link_url:string;
}

export interface MenuFormDataType {
  id?: number | string;
  parent: number | string;
  name: string;
  component: string;
  web_path: string;
  icon: string;
  cache: boolean;
  status: boolean;
  visible: boolean;
  component_name: string;
  description: string;
  is_catalog: boolean;
  is_link: boolean;
  is_iframe:boolean;
  is_affix:boolean;
  link_url: string|undefined;
}
