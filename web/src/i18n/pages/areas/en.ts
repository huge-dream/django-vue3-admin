// Define content
export default {
    message: {
        pages: {
            areas: {
                table: {
                    columns: {
                        index: 'No.',
                        areaName: 'Area Name',
                        areaCode: 'Area Code',
                        parentArea: 'Parent Area',
                        sort: 'Sort',
                        status: 'Status',
                        createTime: 'Create Time',
                        actions: 'Actions',
                    },
                },
                form: {
                    areaName: 'Area Name',
                    areaCode: 'Area Code',
                    parentArea: 'Parent Area',
                    sort: 'Sort',
                    status: 'Status',
                    areaNamePlaceholder: 'Enter area name',
                    areaCodePlaceholder: 'Enter area code',
                    sortPlaceholder: 'Enter sort',
                },
                validation: {
                    areaNameRequired: 'Area name is required',
                    areaNameMaxLength: 'Area name must be 50 characters or less',
                    areaNameDuplicate: 'Area name already exists',
                    areaCodeRequired: 'Area code is required',
                    areaCodeMaxLength: 'Area code must be 50 characters or less',
                    areaCodeFormat: 'Invalid area code format',
                    areaCodeDuplicate: 'Area code already exists',
                },
                dialog: {
                    addArea: 'Add Area',
                    editArea: 'Edit Area',
                    deleteConfirm: 'Delete this area?',
                },
                messages: {
                    addSuccess: 'Added successfully',
                    updateSuccess: 'Updated successfully',
                    deleteSuccess: 'Deleted successfully',
                    deleteFailed: 'Delete failed',
                },
                buttons: {
                    add: 'Add',
                    edit: 'Edit',
                    delete: 'Delete',
                    save: 'Save',
                    cancel: 'Cancel',
                    query: 'Query',
                    refresh: 'Refresh',
                    expandAll: 'Expand All',
                    collapseAll: 'Collapse All',
                },
            },
        },
    },
};
