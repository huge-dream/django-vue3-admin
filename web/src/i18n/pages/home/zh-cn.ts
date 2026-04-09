// 定义内容
export default {
    message: {
        pages: {
            home: {
                statCards: {
                    orderStats: '订单统计信息',
                    monthlyPlan: '月度计划信息',
                    visitStats: '访问统计信息',
                },
                chart: {
                    // Line chart (政策补贴额度)
                    lineTitle: '政策补贴额度',
                    lineLegendPreOrder: '预购队列',
                    lineLegendLatestPrice: '最新成交价',
                    lineYAxisName: '价格',
                    month: '月',
                    // Pie chart (房屋建筑工程)
                    pieTitle: '房屋建筑工程',
                    pieCategory1: '房屋及结构物',
                    pieCategory2: '专用设备',
                    pieCategory3: '通用设备',
                    pieCategory4: '文物和陈列品',
                    pieCategory5: '图书、档案',
                    // Bar chart (地热开发利用)
                    barTitle: '地热开发利用',
                    barLegendSupplyTemp: '供温',
                    barLegendReturnTemp: '回温',
                    barLegendPressure: '压力值(Mpa)',
                    barYAxisSupplyReturn: '供回温度(℃)',
                },
                quickNav: {
                    quickNavTitle: '快捷导航工具',
                },
                notifications: {
                    defaultCreator: '未知用户',
                },
                buyerDashboard: {
                    roleSwitch: {
                        buyer: '采购方仪表盘',
                        supplier: '供应商仪表盘',
                    },
                    kpi: {
                        totalInquiries: '已完成询价单总数',
                        pendingInquiries: '进行中询价单',
                        quoteTimelyRate: '供应商报价及时率',
                        trendUp: '较上月 +12%',
                        trendFlat: '持平',
                    },
                    task: {
                        title: '我的待办任务',
                        empty: '暂无待办任务',
                        table: {
                            columns: {
                                inquiryNo: '询价单号',
                                method: '采购方式',
                                name: '询价单名称',
                                status: '当前状态',
                                deadline: '截止时间 / 剩余时间',
                                action: '操作',
                            },
                        },
                        status: {
                            bidCompare: '比价',
                            published: '发布',
                            negotiation: '议价',
                            urgent: '紧急',
                            default: '',
                        },
                        action: {
                            goBidCompare: '去比价',
                            goNegotiate: '去议价',
                            viewDetail: '查看详情',
                        },
                    },
                    deadline: {
                        bidTime: '投标时间：',
                        quoteDeadline: '报价截止时间：',
                        remaining: '剩余：',
                        bidInProgress: '投标进行中',
                        ended: '已结束',
                        started: '已开始',
                        expired: '已到期',
                    },
                    notification: {
                        title: '系统通知',
                        empty: '暂无通知',
                        defaultCreator: '未知用户',
                    },
                    quickNav: {
                        title: '快捷入口',
                        items: {
                            role: '角色管理',
                            dept: '部门管理',
                            config: '系统配置',
                            dictionary: '字典管理',
                            areas: '区域管理',
                            message: '消息中心',
                        },
                    },
                    chart: {
                        title: '近30天业务趋势',
                        legend: {
                            publishInquiry: '发布询价',
                            negotiationComplete: '议价完成',
                        },
                        yAxisName: '单据数量',
                    },
                    viewAll: '查看全部',
                    more: '更多',
                    method: {
                        inquiry: '询价',
                        tender: '招标',
                    },
                },
                supplierDashboard: {
                    kpi: {
                        totalQuotes: '报价单总数',
                        pendingQuotes: '待报价',
                        wonQuotes: '已中标',
                        conversionRate: '中标率',
                        trendUp: '较上月 +8%',
                        waiting: '等待报价',
                        winSuccess: '中标成功',
                        trendFlat: '持平',
                    },
                    quoteList: {
                        title: '待报价清单',
                        empty: '暂无待报价清单',
                        columns: {
                            inquiryNo: '询价单号',
                            status: '状态',
                            method: '采购方式',
                            deadline: '截止时间',
                            action: '操作',
                        },
                        productName: '产品名称',
                        quantity: '数量',
                    },
                    quoteStatus: {
                        unquoted: '未报价',
                        quoting: '报价中',
                        quoted: '已报价',
                    },
                    quoteAction: {
                        goQuote: '去报价',
                    },
                    notification: {
                        title: '系统通知',
                        empty: '暂无通知',
                        defaultCreator: '未知用户',
                    },
                    quickNav: {
                        title: '快捷入口',
                        items: {
                            role: '角色管理',
                            dept: '部门管理',
                            config: '系统配置',
                            dictionary: '字典管理',
                            areas: '区域管理',
                            message: '消息中心',
                        },
                    },
                    chart: {
                        title: '报价与中标趋势',
                        legend: {
                            quotes: '报价数',
                            won: '中标数',
                        },
                        yAxisName: '单据数量',
                    },
                    viewAll: '查看全部',
                    more: '更多',
                    method: {
                        inquiry: '询价',
                        tender: '招标',
                    },
                },
            },
        },
    },
};
