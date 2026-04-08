import { defineStore } from 'pinia';

export interface DataItemType {
	field_name: string;
	is_create: boolean;
	is_query: boolean;
	is_update: boolean;
}

export const useColumnPermission = defineStore('columnPermission', {
	state: () => ({
		permission: [] as DataItemType[],
	}),

	actions: {
		setPermissionData(data: DataItemType[]) {
			this.permission = data;
		},
	},
});
