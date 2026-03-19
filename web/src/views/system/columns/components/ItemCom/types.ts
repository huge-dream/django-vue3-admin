export interface PageQuery {
  page: number;
  limit: number;
}

export interface RoleItemType {
  id: number | string;
  modifier_name: string;
  creator_name: string;
  create_datetime: string;
  update_datetime: string;
  description: string;
  modifier: string;
  dept_belong_id: number | string | null,
  name: string;
  key: string;
  sort: number;
  status: boolean;
  admin: boolean;
  creator: string;
}

export interface RoleInfoStateType {
  current: string;
  page: number;
  limit: number;
  data: any[],
  total: number;
}