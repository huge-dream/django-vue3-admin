// 定义内容
export default {
    message: {
        pages: {
            rfs_operation_logs: {
                operationType: {
                    1: '询价单创建',
                    2: '询价单确认',
                    3: '询价单发布',
                    4: '询价单还原',
                    5: '报价截止',
                    6: '供应商报价',
                    7: '比议价',
                    8: '议价审核提交',
                    9: '议价审核完成',
                    10: '议价审核驳回',
                },
                purchaseType: {
                    1: '策采',
                    2: '杂采',
                },
                table: {
                    columns: {
                        inquiry_no: '询价单号',
                        buyer: '采购负责人',
                        purchase_type: '采购类别',
                        operation_time: '操作时间',
                        operation_type: '操作类型',
                        operation_user: '操作人',
                        status_change: '状态变更',
                        operation_desc: '操作描述',
                        quotation_no: '报价单号',
                    },
                },
                placeholder: {
                    inquiry_no: '请输入询价单号',
                    buyer: '请输入采购负责人',
                },
                formatter: {
                    empty: '—',
                    noQuotation: '—',
                },
            },
        },
    },
};
