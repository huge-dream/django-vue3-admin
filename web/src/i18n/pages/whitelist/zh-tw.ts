// 定義內容
export default {
    message: {
        pages: {
            whitelist: {
                table: {
                    columns: {
                        url: 'URL',
                        description: '描述',
                        status: '狀態',
                        createTime: '創建時間',
                        creator: '創建人',
                        actions: '操作',
                        index: '序號',
                        keyword: '關鍵詞',
                        method: '請求方式',
                        dataPermission: '資料權限',
                    },
                },
                form: {
                    url: 'URL',
                    description: '描述',
                    status: '狀態',
                    urlPlaceholder: '請輸入URL',
                    descriptionPlaceholder: '請輸入描述',
                    keywordPlaceholder: '請輸入關鍵詞',
                    urlHelper: '支援模糊匹配，如 /api/user/* 可匹配 /api/user/1、/api/user/2',
                },
                validation: {
                    urlRequired: '請輸入URL',
                    urlMaxLength: 'URL不能超過200個字符',
                    urlFormat: 'URL格式不正確',
                    urlDuplicate: 'URL已存在',
                    methodRequired: '請選擇請求方式',
                },
                dialog: {
                    addWhiteList: '新增白名單',
                    editWhiteList: '編輯白名單',
                    deleteConfirm: '確定刪除該白名單嗎？',
                },
                messages: {
                    addSuccess: '新增成功',
                    updateSuccess: '更新成功',
                    deleteSuccess: '刪除成功',
                    deleteFailed: '刪除失敗',
                },
                buttons: {
                    add: '新增',
                    edit: '編輯',
                    delete: '刪除',
                    save: '保存',
                    cancel: '取消',
                    query: '查詢',
                    refresh: '刷新',
                    export: '導出',
                },
            },
        },
    },
};
