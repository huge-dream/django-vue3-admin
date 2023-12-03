import { useColumnPermission } from '/@/stores/columnPermission';

type permissionType = 'is_create' | 'is_query' | 'is_update';

export const columnPermission = (key: string, type: permissionType): boolean => {
	const permissions = useColumnPermission().permission || [];

	return !!permissions.some((i) => i.field_name === key && i[type]);
};

/**
 * 处理字段权限
 * @param crudOptions
 */
export const handleColumnPermission = async (crudOptions:any)=>{
	const res = await GetPermission();
	const columns = crudOptions.columns;
	for(let col in columns){
		if(columns[col].column){
			columns[col].column.show = false
		}else{
			columns[col]['column'] = {
				show:false
			}
		}
		columns[col].addForm = {
			show:false
		}
		columns[col].editForm = {
			show:false
		}
		for(let item of res.data){
			if(item.field_name === col){
				columns[col].column.show = item['is_query']
				columns[col].addForm = {
					show:item['is_create']
				}
				columns[col].editForm = {
					show:item['is_update']
				}
				break;
			}
		}
	}
	return columns
}
