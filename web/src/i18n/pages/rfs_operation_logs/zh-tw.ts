// 定義內容
export default {
    message: {
        pages: {
            rfs_operation_logs: {
                operationType: {
                    1: '詢價單創建',
                    2: '詢價單確認',
                    3: '詢價單發布',
                    4: '詢價單還原',
                    5: '報價截止',
                    6: '供應商報價',
                    7: '比議價',
                    8: '議價審核提交',
                    9: '議價審核完成',
                    10: '議價審核駁回',
                },
                purchaseType: {
                    1: '策採',
                    2: '雜採',
                },
                table: {
                    columns: {
                        inquiry_no: '詢價單號',
                        buyer: '採購負責人',
                        purchase_type: '採購類別',
                        operation_time: '操作時間',
                        operation_type: '操作類型',
                        operation_user: '操作人',
                        status_change: '狀態變更',
                        operation_desc: '操作描述',
                        quotation_no: '報價單號',
                    },
                },
                placeholder: {
                    inquiry_no: '請輸入詢價單號',
                    buyer: '請輸入採購負責人',
                },
                formatter: {
                    empty: '—',
                    noQuotation: '—',
                },
            },
        },
    },
};
