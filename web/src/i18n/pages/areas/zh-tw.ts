// 定義內容
export default {
    message: {
        pages: {
            areas: {
                table: {
                    columns: {
                        index: '序號',
                        areaName: '區域名稱',
                        areaCode: '區域編碼',
                        parentArea: '上級區域',
                        sort: '排序',
                        status: '狀態',
                        createTime: '創建時間',
                        actions: '操作',
                    },
                },
                form: {
                    areaName: '區域名稱',
                    areaCode: '區域編碼',
                    parentArea: '上級區域',
                    sort: '排序',
                    status: '狀態',
                    areaNamePlaceholder: '請輸入區域名稱',
                    areaCodePlaceholder: '請輸入區域編碼',
                    sortPlaceholder: '請輸入排序',
                },
                validation: {
                    areaNameRequired: '區域名稱必填',
                    areaNameMaxLength: '區域名稱不能超過50個字符',
                    areaNameDuplicate: '區域名稱已存在',
                    areaCodeRequired: '區域編碼必填',
                    areaCodeMaxLength: '區域編碼不能超過50個字符',
                    areaCodeFormat: '區域編碼格式不正確',
                    areaCodeDuplicate: '區域編碼已存在',
                },
                dialog: {
                    addArea: '新增區域',
                    editArea: '編輯區域',
                    deleteConfirm: '確定刪除該區域嗎？',
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
                    expandAll: '展開全部',
                    collapseAll: '收起全部',
                },
            },
        },
    },
};
