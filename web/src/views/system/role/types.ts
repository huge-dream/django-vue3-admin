/**角色列表数据类型 */
export interface RoleItemType {
	id: string | number;
	modifier_name: string;
	creator_name: string;
	create_datetime: string;
	update_datetime: string;
	description: string;
	modifier: string;
	dept_belong_id: string;
	name: string;
	key: string;
	sort: number;
	status: boolean;
	admin: boolean;
	creator: string;
}

export interface UsersType {
	id: string | number;
	name: string;
}
export interface RoleUsersType {
	all_users: UsersType[];
	right_users: UsersType[];
}

/**
 * 权限配置 抽屉组件参数数据类型
 */
export interface RoleDrawerType {
	/** 是否显示抽屉*/
	drawerVisible: boolean;
	/** 角色id*/
	roleId: string | number | undefined;
	/** 角色名称*/
	roleName: string | undefined;
	/** 用户*/
	users: UsersType[];
}

/**
 * 菜单数据类型
 */
export interface RoleMenuTreeType {
	id: number | string | undefined;
	/** 父级id */
	parent: number | string | undefined;
	name: string;
	/** 是否选中 */
	isCheck: boolean;
	/** 是否是目录 */
	is_catalog: boolean;
}
/**
 * 菜单-按钮数据类型
 */
export interface RoleMenuBtnType {
	id: string | number;
	menu_btn_pre_id: string | number;
	/** 是否选中 */
	isCheck: boolean;
	/** 按钮名称 */
	name: string;
	/** 数据权限范围 */
	data_range: number | null;
	/** 自定义部门 */
	dept: number[];
}

/**
 * 菜单-列字段数据类型
 */
export interface RoleMenuFieldType {
	id: string | number | boolean;
	/** 模型表字段名 */
	field_name: string;
	/** 字段显示名	*/
	title: string;
	/** 是否可查询 */
	is_query: boolean;
	/** 是否可创建 */
	is_create: boolean;
	/** 是否可更新 */
	is_update: boolean;
	[key: string]: string | number | boolean;
}
/**
 * 菜单-列字段-标题数据类型
 */
export interface RoleMenuFieldHeaderType {
	value: string;
	/** 模型表字段名 */
	label: string;
	/** 字段显示名	*/
	disabled: string;
	/** 是否可查询 */
	checked: boolean;
}
