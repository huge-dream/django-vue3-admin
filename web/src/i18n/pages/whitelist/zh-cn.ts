// 定义内容
export default {
    message: {
        pages: {
            whitelist: {
                table: {
                    columns: {
                        url: 'URL',
                        description: '描述',
                        status: '状态',
                        createTime: '创建时间',
                        creator: '创建人',
                        actions: '操作',
                        index: '序号',
                        keyword: '关键词',
                        method: '请求方法',
                        dataPermission: '数据权限',
                    },
                },
                form: {
                    url: 'URL',
                    description: '描述',
                    status: '状态',
                    urlPlaceholder: '请输入URL',
                    descriptionPlaceholder: '请输入描述',
                    keywordPlaceholder: '请输入关键词',
                    urlHelper: '支持模糊匹配，如 /api/user/* 可匹配 /api/user/1、/api/user/2',
                },
                validation: {
                    urlRequired: '请输入URL',
                    urlMaxLength: 'URL不能超过200个字符',
                    urlFormat: 'URL格式不正确',
                    urlDuplicate: 'URL已存在',
                    methodRequired: '请选择请求方法',
                },
                dialog: {
                    addWhiteList: '新增白名单',
                    editWhiteList: '编辑白名单',
                    deleteConfirm: '确定删除该白名单吗？',
                },
                messages: {
                    addSuccess: '新增成功',
                    updateSuccess: '更新成功',
                    deleteSuccess: '删除成功',
                    deleteFailed: '删除失败',
                },
                buttons: {
                    add: '新增',
                    edit: '编辑',
                    delete: '删除',
                    save: '保存',
                    cancel: '取消',
                    query: '查询',
                    refresh: '刷新',
                    export: '导出',
                },
            },
        },
    },
};
