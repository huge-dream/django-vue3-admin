// 定义内容
export default {
    message: {
        pages: {
            taskLog: {
                table: {
                    columns: {
                        index: '序号',
                        taskId: '任务ID',
                        taskName: '任务名称',
                        periodicTaskName: '周期任务名称',
                        taskKwargs: '请求参数',
                        status: '执行状态',
                        result: '执行结果',
                        dateDone: '执行完成时间',
                        dateCreated: '创建时间',
                    },
                },
                status: {
                    SUCCESS: '执行成功',
                    STARTED: '已开始',
                    REVOKED: '已取消',
                    RETRY: '重试中',
                    RECEIVED: '已收到',
                    PENDING: '待定中',
                    FAILURE: '执行失败',
                },
                buttons: {
                    view: '查看',
                },
            },
        },
    },
};
