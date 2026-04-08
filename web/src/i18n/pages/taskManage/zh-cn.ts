// 定义内容
export default {
    message: {
        pages: {
            taskManage: {
                table: {
                    columns: {
                        index: '序号',
                        name: '任务名称',
                        task: '执行任务',
                        lastRunAt: '最后运行时间',
                        description: '备注',
                        cron: '表达式',
                        kwargs: '请求参数',
                        status: '状态',
                        enabled: '启用',
                        disabled: '禁用',
                    },
                },
                form: {
                    name: '任务名称',
                    namePlaceholder: '请输入任务名称',
                    task: '执行任务',
                    taskPlaceholder: '输入执行任务',
                    cron: 'Cron表达式设置',
                    cronExpression: 'Cron表达式',
                    lastRunAt: '最后运行时间',
                    description: '备注',
                    kwargs: '请求参数',
                    enabled: '状态',
                    validation: {
                        nameRequired: '任务名称必填',
                        taskRequired: '执行任务必填',
                        cronRequired: '表达式必填',
                        statusRequired: '排序必填',
                    },
                },
                dialog: {
                    taskLogs: '任务运行日志',
                    cronSelector: 'Cron表达式选择器',
                    confirmStop: '确认停用该任务？',
                    confirmEnable: '确认启用该任务？',
                    confirmRun: '立即运行该任务？',
                    confirmDelete: '确定删除该任务？',
                },
                messages: {
                    enableSuccess: '任务已启用',
                    disableSuccess: '任务已停用',
                    runSuccess: '任务已触发执行',
                    deleteSuccess: '任务已删除',
                },
                buttons: {
                    view: '查看',
                    edit: '编辑',
                    delete: '删除',
                    add: '新增',
                    confirm: '确定',
                    cancel: '取消',
                    enable: '已启用',
                    disabled: '已停用',
                    runNow: '立即运行',
                    taskLogs: '任务日志',
                },
                card: {
                    executeTask: '执行任务',
                    cronRule: '定时规则',
                    lastRunTime: '最后运行时间',
                },
                empty: '暂无数据，请添加',
            },
        },
    },
};
