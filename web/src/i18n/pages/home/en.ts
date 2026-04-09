// Define content
export default {
    message: {
        pages: {
            home: {
                statCards: {
                    orderStats: 'Order Statistics',
                    monthlyPlan: 'Monthly Plan Info',
                    visitStats: 'Visit Statistics',
                },
                chart: {
                    // Line chart (政策补贴额度)
                    lineTitle: 'Policy Subsidy Quota',
                    lineLegendPreOrder: 'Pre-Order Queue',
                    lineLegendLatestPrice: 'Latest Transaction Price',
                    lineYAxisName: 'Price',
                    month: '',
                    // Pie chart (房屋建筑工程)
                    pieTitle: 'Building & Structural Engineering',
                    pieCategory1: 'Buildings & Structures',
                    pieCategory2: 'Special Equipment',
                    pieCategory3: 'General Equipment',
                    pieCategory4: 'Cultural Relics & Exhibits',
                    pieCategory5: 'Books & Archives',
                    // Bar chart (地热开发利用)
                    barTitle: 'Geothermal Development & Utilization',
                    barLegendSupplyTemp: 'Supply Temperature',
                    barLegendReturnTemp: 'Return Temperature',
                    barLegendPressure: 'Pressure (Mpa)',
                    barYAxisSupplyReturn: 'Supply/Return Temp (℃)',
                },
                quickNav: {
                    quickNavTitle: 'Quick Navigation',
                },
                notifications: {
                    defaultCreator: 'Unknown User',
                },
                buyerDashboard: {
                    roleSwitch: {
                        buyer: 'Buyer Dashboard',
                        supplier: 'Supplier Dashboard',
                    },
                    kpi: {
                        totalInquiries: 'Total Completed Inquiries',
                        pendingInquiries: 'Pending Inquiries',
                        quoteTimelyRate: 'Quote Timely Rate',
                        trendUp: '+12% vs last month',
                        trendFlat: 'Flat',
                    },
                    task: {
                        title: 'My Tasks',
                        empty: 'No pending tasks',
                        table: {
                            columns: {
                                inquiryNo: 'Inquiry No.',
                                method: 'Procurement Method',
                                name: 'Inquiry Name',
                                status: 'Status',
                                deadline: 'Deadline / Remaining',
                                action: 'Action',
                            },
                        },
                        status: {
                            bidCompare: 'Bid Comparison',
                            published: 'Published',
                            negotiation: 'Negotiation',
                            urgent: 'Urgent',
                            default: '',
                        },
                        action: {
                            goBidCompare: 'Go to Compare',
                            goNegotiate: 'Go to Negotiate',
                            viewDetail: 'View Details',
                        },
                    },
                    deadline: {
                        bidTime: 'Bid Time:',
                        quoteDeadline: 'Quote Deadline:',
                        remaining: 'Remaining:',
                        bidInProgress: 'Bid in Progress',
                        ended: 'Ended',
                        started: 'Started',
                        expired: 'Expired',
                    },
                    notification: {
                        title: 'System Notifications',
                        empty: 'No notifications',
                        defaultCreator: 'Unknown User',
                    },
                    quickNav: {
                        title: 'Quick Navigation',
                        items: {
                            role: 'Role Management',
                            dept: 'Department Management',
                            config: 'System Config',
                            dictionary: 'Dictionary Management',
                            areas: 'Area Management',
                            message: 'Message Center',
                        },
                    },
                    chart: {
                        title: 'Last 30 Days Trend',
                        legend: {
                            publishInquiry: 'Inquiries Published',
                            negotiationComplete: 'Negotiations Complete',
                        },
                        yAxisName: 'Count',
                    },
                    viewAll: 'View All',
                    more: 'More',
                    method: {
                        inquiry: 'Inquiry',
                        tender: 'Tender',
                    },
                },
                supplierDashboard: {
                    kpi: {
                        totalQuotes: 'Total Quotes',
                        pendingQuotes: 'Pending Quotes',
                        wonQuotes: 'Won Quotes',
                        conversionRate: 'Win Rate',
                        trendUp: '+8% vs last month',
                        waiting: 'Awaiting Quote',
                        winSuccess: 'Won Successfully',
                        trendFlat: 'Flat',
                    },
                    quoteList: {
                        title: 'Pending Quote List',
                        empty: 'No pending quotes',
                        columns: {
                            inquiryNo: 'Inquiry No.',
                            status: 'Status',
                            method: 'Procurement Method',
                            deadline: 'Deadline',
                            action: 'Action',
                        },
                        productName: 'Product Name',
                        quantity: 'Quantity',
                    },
                    quoteStatus: {
                        unquoted: 'Unquoted',
                        quoting: 'Quoting',
                        quoted: 'Quoted',
                    },
                    quoteAction: {
                        goQuote: 'Go to Quote',
                    },
                    notification: {
                        title: 'System Notifications',
                        empty: 'No notifications',
                        defaultCreator: 'Unknown User',
                    },
                    quickNav: {
                        title: 'Quick Navigation',
                        items: {
                            role: 'Role Management',
                            dept: 'Department Management',
                            config: 'System Config',
                            dictionary: 'Dictionary Management',
                            areas: 'Area Management',
                            message: 'Message Center',
                        },
                    },
                    chart: {
                        title: 'Quote & Win Trend',
                        legend: {
                            quotes: 'Quotes',
                            won: 'Won',
                        },
                        yAxisName: 'Count',
                    },
                    viewAll: 'View All',
                    more: 'More',
                    method: {
                        inquiry: 'Inquiry',
                        tender: 'Tender',
                    },
                },
            },
        },
    },
};
