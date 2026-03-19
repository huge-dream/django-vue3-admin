export interface TreeType {
  id: number;
  name: string;
  status: boolean;
  children?: TreeType[];
}

export interface APIResponseData {
  code?: number;
  data: [];
  msg?: string;
}

export interface FormType<T> {
  [key: string]: T;
}

export interface TreeItemType {
  id?: number | string;
  modifier_name?: string;
  creator_name?: string;
  create_datetime?: string;
  update_datetime?: string;
  parent_name?: string;
  status_label?: string;
  has_children?: number;
  hasChild?: false,
  description?: string;
  modifier?: string;
  dept_belong_id?: string;
  name?: string;
  key?: string;
  sort?: number;
  owner?: string;
  phone?: string;
  email?: string;
  status?: boolean;
  creator?: number;
  parent?: number;
}

export interface DeptFormDataType {
  id?: string | number;
  key: string;
  parent: string | number;
  name: string;
  owner: string;
  description: string;
}

export interface DeptListType {
  id: number;
  name: string;
  parent: number;
}

export interface HeadDeptInfoType {
  dept_name: string;
  dept_user: number;
  owner: string;
  description: string;
  gender: {
    male: number;
    female: number;
    unknown: number;
  };
  sub_dept_map: { name: string; count: number }[]
}