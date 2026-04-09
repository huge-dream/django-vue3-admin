// Define content
export default {
    message: {
        pages: {
            taskLog: {
                table: {
                    columns: {
                        index: 'No.',
                        taskId: 'Task ID',
                        taskName: 'Task Name',
                        periodicTaskName: 'Periodic Task Name',
                        taskKwargs: 'Parameters',
                        status: 'Status',
                        result: 'Result',
                        dateDone: 'Completed At',
                        dateCreated: 'Created At',
                    },
                },
                status: {
                    SUCCESS: 'Success',
                    STARTED: 'Started',
                    REVOKED: 'Revoked',
                    RETRY: 'Retrying',
                    RECEIVED: 'Received',
                    PENDING: 'Pending',
                    FAILURE: 'Failure',
                },
                buttons: {
                    view: 'View',
                },
            },
        },
    },
};
