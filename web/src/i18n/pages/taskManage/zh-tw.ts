// 定義內容
export default {
    message: {
        pages: {
            taskManage: {
                table: {
                    columns: {
                        index: '序號',
                        name: '任務名稱',
                        task: '執行任務',
                        lastRunAt: '最後運行時間',
                        description: '備註',
                        cron: '表達式',
                        kwargs: '請求參數',
                        status: '狀態',
                        enabled: '啟用',
                        disabled: '禁用',
                    },
                },
                form: {
                    name: '任務名稱',
                    namePlaceholder: '請輸入任務名稱',
                    task: '執行任務',
                    taskPlaceholder: '輸入執行任務',
                    cron: 'Cron表達式設置',
                    cronExpression: 'Cron表達式',
                    lastRunAt: '最後運行時間',
                    description: '備註',
                    kwargs: '請求參數',
                    enabled: '狀態',
                    validation: {
                        nameRequired: '任務名稱必填',
                        taskRequired: '執行任務必填',
                        cronRequired: '表達式必填',
                        statusRequired: '排序必填',
                    },
                },
                dialog: {
                    taskLogs: '任務運行日誌',
                    cronSelector: 'Cron表達式選擇器',
                    confirmStop: '確認停用該任務？',
                    confirmEnable: '確認啟用該任務？',
                    confirmRun: '立即運行該任務？',
                    confirmDelete: '確定刪除該任務？',
                },
                messages: {
                    enableSuccess: '任務已啟用',
                    disableSuccess: '任務已停用',
                    runSuccess: '任務已觸發執行',
                    deleteSuccess: '任務已刪除',
                },
                buttons: {
                    view: '查看',
                    edit: '編輯',
                    delete: '刪除',
                    add: '新增',
                    confirm: '確定',
                    cancel: '取消',
                    enable: '已啟用',
                    disabled: '已停用',
                    runNow: '立即運行',
                    taskLogs: '任務日誌',
                },
                card: {
                    executeTask: '執行任務',
                    cronRule: '定時規則',
                    lastRunTime: '最後運行時間',
                },
                empty: '暫無數據，請添加',
            },
        },
    },
};
