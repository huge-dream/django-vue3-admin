// Define content
export default {
    message: {
        pages: {
            taskManage: {
                table: {
                    columns: {
                        index: 'No.',
                        name: 'Task Name',
                        task: 'Task',
                        lastRunAt: 'Last Run',
                        description: 'Description',
                        cron: 'Cron Expression',
                        kwargs: 'Parameters',
                        status: 'Status',
                        enabled: 'Enabled',
                        disabled: 'Disabled',
                    },
                },
                form: {
                    name: 'Task Name',
                    namePlaceholder: 'Please enter task name',
                    task: 'Task',
                    taskPlaceholder: 'Input task',
                    cron: 'Cron Expression Settings',
                    cronExpression: 'Cron Expression',
                    lastRunAt: 'Last Run',
                    description: 'Description',
                    kwargs: 'Parameters',
                    enabled: 'Status',
                    validation: {
                        nameRequired: 'Task name is required',
                        taskRequired: 'Task is required',
                        cronRequired: 'Expression is required',
                        statusRequired: 'Status is required',
                    },
                },
                dialog: {
                    taskLogs: 'Task Execution Logs',
                    cronSelector: 'Cron Expression Selector',
                    confirmStop: 'Confirm to disable this task?',
                    confirmEnable: 'Confirm to enable this task?',
                    confirmRun: 'Run this task immediately?',
                    confirmDelete: 'Confirm to delete this task?',
                },
                messages: {
                    enableSuccess: 'Task enabled',
                    disableSuccess: 'Task disabled',
                    runSuccess: 'Task triggered',
                    deleteSuccess: 'Task deleted',
                },
                buttons: {
                    view: 'View',
                    edit: 'Edit',
                    delete: 'Delete',
                    add: 'Add',
                    confirm: 'Confirm',
                    cancel: 'Cancel',
                    enable: 'Enabled',
                    disabled: 'Disabled',
                    runNow: 'Run Now',
                    taskLogs: 'Task Logs',
                },
                card: {
                    executeTask: 'Execute Task',
                    cronRule: 'Cron Rule',
                    lastRunTime: 'Last Run Time',
                },
                empty: 'No data, please add',
            },
        },
    },
};
