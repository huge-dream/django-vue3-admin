export interface DataPermissionRangeType {
	label: string;
	value: number;
}

export interface CustomDataPermissionDeptType {
	id: number;
	name: string;
	patent: number;
	children: CustomDataPermissionDeptType[];
}

export interface CustomDataPermissionMenuType {
	id: number;
	name: string;
	is_catalog: boolean;
	menuPermission: { id: number; name: string; value: string }[] | null;
	columns: { id: number; name: string; title: string }[] | null;
	children: CustomDataPermissionMenuType[];
}

export interface MenuDataType {
	id: string;
	name: string;
	isCheck: boolean;
	btns: { id: number; name: string; value: string; isCheck: boolean; data_range: number; dept: object }[];
	columns: { [key: string]: boolean | string; }[];
	children: MenuDataType[];
}
