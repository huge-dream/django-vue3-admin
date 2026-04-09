// Define content
export default {
    message: {
        pages: {
            home: {
                statCards: {
                    orderStats: '訂單統計信息',
                    monthlyPlan: '月度計劃信息',
                    visitStats: '訪問統計信息',
                },
                chart: {
                    // Line chart (政策补贴额度)
                    lineTitle: '政策補貼額度',
                    lineLegendPreOrder: '預購隊列',
                    lineLegendLatestPrice: '最新成交價',
                    lineYAxisName: '價格',
                    month: '月',
                    // Pie chart (房屋建筑工程)
                    pieTitle: '房屋建築工程',
                    pieCategory1: '房屋及結構物',
                    pieCategory2: '專用設備',
                    pieCategory3: '通用設備',
                    pieCategory4: '文物和陳列品',
                    pieCategory5: '圖書、檔案',
                    // Bar chart (地热开发利用)
                    barTitle: '地熱開發利用',
                    barLegendSupplyTemp: '供溫',
                    barLegendReturnTemp: '回溫',
                    barLegendPressure: '壓力值(Mpa)',
                    barYAxisSupplyReturn: '供回溫度(℃)',
                },
                quickNav: {
                    quickNavTitle: '快捷導航工具',
                },
                notifications: {
                    defaultCreator: '未知用戶',
                },
                buyerDashboard: {
                    roleSwitch: {
                        buyer: '採購方儀表盤',
                        supplier: '供應商儀表盤',
                    },
                    kpi: {
                        totalInquiries: '已完成詢價單總數',
                        pendingInquiries: '進行中詢價單',
                        quoteTimelyRate: '供應商報價及時率',
                        trendUp: '較上月 +12%',
                        trendFlat: '持平',
                    },
                    task: {
                        title: '我的待辦任務',
                        empty: '暫無待辦任務',
                        table: {
                            columns: {
                                inquiryNo: '詢價單號',
                                method: '採購方式',
                                name: '詢價單名稱',
                                status: '當前狀態',
                                deadline: '截止時間 / 剩餘時間',
                                action: '操作',
                            },
                        },
                        status: {
                            bidCompare: '比價',
                            published: '發布',
                            negotiation: '議價',
                            urgent: '緊急',
                            default: '',
                        },
                        action: {
                            goBidCompare: '去比價',
                            goNegotiate: '去議價',
                            viewDetail: '查看詳情',
                        },
                    },
                    deadline: {
                        bidTime: '投標時間：',
                        quoteDeadline: '報價截止時間：',
                        remaining: '剩餘：',
                        bidInProgress: '投標進行中',
                        ended: '已結束',
                        started: '已開始',
                        expired: '已到期',
                    },
                    notification: {
                        title: '系統通知',
                        empty: '暫無通知',
                        defaultCreator: '未知用戶',
                    },
                    quickNav: {
                        title: '快捷入口',
                        items: {
                            role: '角色管理',
                            dept: '部門管理',
                            config: '系統配置',
                            dictionary: '字典管理',
                            areas: '區域管理',
                            message: '消息中心',
                        },
                    },
                    chart: {
                        title: '近30天業務趨勢',
                        legend: {
                            publishInquiry: '發布詢價',
                            negotiationComplete: '議價完成',
                        },
                        yAxisName: '單據數量',
                    },
                    viewAll: '查看全部',
                    more: '更多',
                    method: {
                        inquiry: '詢價',
                        tender: '招標',
                    },
                },
                supplierDashboard: {
                    kpi: {
                        totalQuotes: '報價單總數',
                        pendingQuotes: '待報價',
                        wonQuotes: '已中標',
                        conversionRate: '中標率',
                        trendUp: '較上月 +8%',
                        waiting: '等待報價',
                        winSuccess: '中標成功',
                        trendFlat: '持平',
                    },
                    quoteList: {
                        title: '待報價清單',
                        empty: '暫無待報價清單',
                        columns: {
                            inquiryNo: '詢價單號',
                            status: '狀態',
                            method: '採購方式',
                            deadline: '截止時間',
                            action: '操作',
                        },
                        productName: '產品名稱',
                        quantity: '數量',
                    },
                    quoteStatus: {
                        unquoted: '未報價',
                        quoting: '報價中',
                        quoted: '已報價',
                    },
                    quoteAction: {
                        goQuote: '去報價',
                    },
                    notification: {
                        title: '系統通知',
                        empty: '暫無通知',
                        defaultCreator: '未知用戶',
                    },
                    quickNav: {
                        title: '快捷入口',
                        items: {
                            role: '角色管理',
                            dept: '部門管理',
                            config: '系統配置',
                            dictionary: '字典管理',
                            areas: '區域管理',
                            message: '消息中心',
                        },
                    },
                    chart: {
                        title: '報價與中標趨勢',
                        legend: {
                            quotes: '報價數',
                            won: '中標數',
                        },
                        yAxisName: '單據數量',
                    },
                    viewAll: '查看全部',
                    more: '更多',
                    method: {
                        inquiry: '詢價',
                        tender: '招標',
                    },
                },
            },
        },
    },
};
