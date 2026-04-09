// 定義內容
export default {
    message: {
        pages: {
            messageCenter: {
                tabs: {
                    myPublish: '我的發布',
                    myReceive: '我的接收',
                    unread: '未讀',
                    read: '已讀',
                    all: '全部',
                },
                table: {
                    columns: {
                        title: '標題',
                        type: '類型',
                        creatorName: '發送人',
                        createTime: '發送時間',
                        isRead: '狀態',
                        actions: '操作',
                        targetType: '目標類型',
                        targetUser: '目標用戶',
                        targetRole: '目標角色',
                        targetDept: '目標部門',
                        content: '內容',
                    },
                },
                status: {
                    yes: '已讀',
                    no: '未讀',
                },
                targetType: {
                    byUser: '按用戶',
                    byRole: '按角色',
                    byDept: '按部門',
                    notice: '通知公告',
                },
                buttons: {
                    markAllRead: '全部已讀',
                    markRead: '標記已讀',
                    delete: '刪除',
                    refresh: '刷新',
                    view: '查看',
                    export: '導出',
                    add: '新增',
                },
                form: {
                    titlePlaceholder: '請輸入標題',
                    phone: '用戶電話',
                    roleName: '角色名稱',
                    roleKey: '權限標識',
                    deptName: '部門名稱',
                    status: '狀態',
                    parentDept: '父級部門',
                },
                validation: {
                    titleRequired: '標題必填',
                    targetTypeRequired: '請選擇目標類型',
                    required: '必填項',
                },
                messages: {
                    markReadSuccess: '標記成功',
                    deleteSuccess: '刪除成功',
                },
            },
        },
    },
};
