// Define content
export default {
    message: {
        pages: {
            whitelist: {
                table: {
                    columns: {
                        url: 'URL',
                        description: 'Description',
                        status: 'Status',
                        createTime: 'Create Time',
                        creator: 'Created By',
                        actions: 'Actions',
                        index: 'No.',
                        keyword: 'Keyword',
                        method: 'Method',
                        dataPermission: 'Data Permission',
                    },
                },
                form: {
                    url: 'URL',
                    description: 'Description',
                    status: 'Status',
                    urlPlaceholder: 'Enter URL',
                    descriptionPlaceholder: 'Enter description',
                    keywordPlaceholder: 'Enter keyword',
                    urlHelper: 'Supports fuzzy matching, e.g. /api/user/* matches /api/user/1, /api/user/2',
                },
                validation: {
                    urlRequired: 'URL is required',
                    urlMaxLength: 'URL must be 200 characters or less',
                    urlFormat: 'Invalid URL format',
                    urlDuplicate: 'URL already exists',
                    methodRequired: 'Please select a request method',
                },
                dialog: {
                    addWhiteList: 'Add Whitelist',
                    editWhiteList: 'Edit Whitelist',
                    deleteConfirm: 'Delete this whitelist entry?',
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
                    export: 'Export',
                },
            },
        },
    },
};
