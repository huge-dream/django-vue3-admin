// Define content
export default {
    message: {
        pages: {
            rfs_operation_logs: {
                operationType: {
                    1: 'RFQ Created',
                    2: 'RFQ Confirmed',
                    3: 'RFQ Published',
                    4: 'RFQ Restored',
                    5: 'Quotation Closed',
                    6: 'Supplier Quoted',
                    7: 'Price Comparison',
                    8: 'Negotiation Submitted',
                    9: 'Negotiation Approved',
                    10: 'Negotiation Rejected',
                },
                purchaseType: {
                    1: 'Strategic',
                    2: 'Miscellaneous',
                },
                table: {
                    columns: {
                        inquiry_no: 'RFQ No.',
                        buyer: 'Buyer',
                        purchase_type: 'Purchase Type',
                        operation_time: 'Operation Time',
                        operation_type: 'Operation Type',
                        operation_user: 'Operator',
                        status_change: 'Status Change',
                        operation_desc: 'Operation Description',
                        quotation_no: 'Quotation No.',
                    },
                },
                placeholder: {
                    inquiry_no: 'Enter RFQ No.',
                    buyer: 'Enter buyer name',
                },
                formatter: {
                    empty: '—',
                    noQuotation: '—',
                },
            },
        },
    },
};
