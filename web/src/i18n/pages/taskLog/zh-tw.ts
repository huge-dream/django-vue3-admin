// 定義內容
export default {
    message: {
        pages: {
            taskLog: {
                table: {
                    columns: {
                        index: '序號',
                        taskId: '任務ID',
                        taskName: '任務名稱',
                        periodicTaskName: '週期任務名稱',
                        taskKwargs: '請求參數',
                        status: '執行狀態',
                        result: '執行結果',
                        dateDone: '執行完成時間',
                        dateCreated: '創建時間',
                    },
                },
                status: {
                    SUCCESS: '執行成功',
                    STARTED: '已開始',
                    REVOKED: '已取消',
                    RETRY: '重試中',
                    RECEIVED: '已收到',
                    PENDING: '待定中',
                    FAILURE: '執行失敗',
                },
                buttons: {
                    view: '查看',
                },
            },
        },
    },
};
