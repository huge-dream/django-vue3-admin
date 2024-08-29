import {useColumnPermission} from '/@/stores/columnPermission';

type permissionType = 'is_create' | 'is_query' | 'is_update';

export const columnPermission = (key: string, type: permissionType): boolean => {
	const permissions = useColumnPermission().permission || [];

	return !!permissions.some((i) => i.field_name === key && i[type]);
};

/**
 * 处理字段信息权限
 * @param func 获取字段信息的接口函数
 * @param crudOptions 原始的crudOptions信息
 * @param excludeColumn 需要排除的列
 */
export const handleColumnPermission = async (func: Function, crudOptions: any,excludeColumn:string[]=[]) => {
	const res = await func();
	if(crudOptions.pagination==undefined){
		crudOptions['pagination'] = {
			show:true
		}
	}
	const columns = crudOptions.columns;
	const excludeColumns = ['checked','_index','id', 'create_datetime', 'update_datetime'].concat(excludeColumn)
	for (let col in columns) {
		for (let item of res.data) {
			if (excludeColumns.includes(item.field_name)) {
				continue
			} else if(item.field_name === col) {
				// 如果列表不可见，则禁止在列设置中选择
                // 只有列表不可见，才修改列配置，这样才不影响默认的配置
				if(!item['is_query']){
                    columns[col].column.show = false
                    columns[col].column.columnSetDisabled = true
                }
				columns[col].addForm = {
					show: item['is_create']
				}
				columns[col].editForm = {
					show: item['is_update']
				}
			}
		}
	}
	return crudOptions
}
