<template>
	<div class="supplier-dashboard">
		<!-- 欢迎语 -->
		<div class="welcome-header">
			<span class="welcome-text">{{ $t('message.home.welcomeInfo') }}{{ userInfo.userInfos.name }}</span>
			<span class="welcome-sub">{{ $t('message.home.welcomeInfo1') }}</span>
		</div>

		<!-- KPI 指标卡片 -->
		<div class="kpi-section">
			<div class="kpi-card green">
				<div class="kpi-icon"><i class="fa fa-file-text-o"></i></div>
				<div class="kpi-title">报价单总数</div>
				<div class="kpi-value">{{ kpi.total_quotes.toLocaleString() }}</div>
				<div class="kpi-trend trend-up"><i class="fa fa-arrow-up"></i> 较上月 +8%</div>
			</div>
			<div class="kpi-card orange">
				<div class="kpi-icon"><i class="fa fa-pencil-square-o"></i></div>
				<div class="kpi-title">待报价</div>
				<div class="kpi-value">{{ kpi.pending_quotes }}</div>
				<div class="kpi-trend">等待报价</div>
			</div>
			<div class="kpi-card gold">
				<div class="kpi-icon"><i class="fa fa-trophy"></i></div>
				<div class="kpi-title">已中标</div>
				<div class="kpi-value">{{ kpi.won_quotes }}</div>
				<div class="kpi-trend trend-up"><i class="fa fa-trophy"></i> 中标成功</div>
			</div>
			<div class="kpi-card blue">
				<div class="kpi-icon"><i class="fa fa-bullseye"></i></div>
				<div class="kpi-title">中标率</div>
				<div class="kpi-value">{{ kpi.conversion_rate }}%</div>
				<div class="kpi-trend trend-flat"><i class="fa fa-minus"></i> 持平</div>
			</div>
		</div>

		<!-- 主体内容区 -->
		<div class="main-container">
			<!-- 左侧：待报价清单 -->
			<div class="card quote-card">
				<div class="card-header">
					<div class="card-title">
						<i class="fa fa-pie-chart" style="color: #2e5bff"></i> 待报价清单(<span style="color: #ef4444; font-weight: 600">{{
							pendingQuotes.length
						}}</span
						>)
					</div>
					<a href="#" class="view-all">查看全部 <i class="fa fa-arrow-right"></i></a>
				</div>
				<div class="quote-list">
					<div v-for="quote in pendingQuotes" :key="quote.id" class="quote-item">
						<div class="quote-row">
							<span class="quote-no">{{ quote.inquiry_no }}</span>
							<span class="quote-status" :class="getQuoteStatusClass(quote.status)">{{ getQuoteStatusText(quote.status) }}</span>
							<span class="method-badge" :class="getMethodClass(quote.method)">{{ getMethodText(quote.method) }}</span>
							<div class="quote-deadline-cell">
								<table class="deadline-inner">
									<tbody>
										<tr>
											<td class="deadline-td-label">{{ getDeadlinePrimaryLabel(quote) }}</td>
											<td class="deadline-td-value">
												<span :class="getDeadlineValueClass(quote)">{{ getDeadlinePrimaryValue(quote) }}</span>
											</td>
										</tr>
										<tr>
											<td class="deadline-td-gap"></td>
											<td class="deadline-td-remaining">
												<span class="deadline-remaining-label">剩余：</span>
												<span :class="getDeadlineValueClass(quote)">{{ getDeadlineRemainingValue(quote) }}</span>
											</td>
										</tr>
									</tbody>
								</table>
							</div>
							<button class="action-btn btn-primary" @click="handleQuote(quote)">去报价</button>
						</div>
						<div class="quote-info-row">
							<div class="quote-info-item">
								<span class="label">产品名称</span>
								<span class="value">{{ quote.item_name || '-' }}</span>
							</div>
							<div class="quote-info-item">
								<span class="label">数量</span>
								<span class="value">{{ quote.quantity || '-' }} {{ quote.unit || '' }}</span>
							</div>
						</div>
					</div>
					<div v-if="pendingQuotes.length === 0" class="empty-cell">暂无待报价清单</div>
				</div>
			</div>

			<!-- 右侧：图片+消息通知 + 快捷入口 -->
			<div class="right-sidebar">
				<!-- 图片卡片 + 消息通知 -->
				<div class="card img-notify-card">
					<div class="img-notify-img">
						<img :src="HomeBg" alt="home-bg" class="home-bg-img" />
					</div>
					<div class="img-notify-list">
						<div class="card-header" style="margin-bottom: 12px">
							<div class="card-title"><i class="fa fa-bullhorn" style="color: #2e5bff"></i> 系统通知</div>
							<a href="#" class="view-all">更多 <i class="fa fa-arrow-right"></i></a>
						</div>
						<div class="notify-item" v-for="(v, k) in newsInfoList" :key="k">
							<div class="notify-icon">
								<i class="fa fa-commenting-o" style="color: #5d8b22"></i>
							</div>
							<div class="notify-content">
								<div class="notify-title-row">
									<span class="notify-title">[{{ v.creator_name }}]</span>
									<span class="notify-time">{{ v.create_datetime }}</span>
								</div>
								<div class="notify-title-text">{{ v.title }}</div>
							</div>
						</div>
						<div v-if="newsInfoList.length === 0" class="empty-notif">暂无通知</div>
					</div>
				</div>

				<!-- 快捷入口 -->
				<div class="card quick-nav-card">
					<div class="card-header">
						<div class="card-title"><i class="fa fa-th-large" style="color: #2e5bff"></i> 快捷入口</div>
					</div>
					<div class="quick-nav-grid">
						<div v-for="(item, index) in quickNavList" :key="index" class="quick-nav-item" @click="handleNavClick(item.url)">
							<div class="quick-nav-icon" :style="{ background: item.bgColor }">
								<i :class="item.icon" :style="{ color: item.iconColor }"></i>
							</div>
							<span class="quick-nav-label">{{ item.label }}</span>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- 底部图表区域 -->
		<div class="card chart-section">
			<div class="card-header">
				<div class="card-title"><i class="fa fa-chart-line" style="color: #2e5bff"></i> 报价与中标趋势</div>
				<div class="chart-legend">
					<span><span class="legend-dot" style="background: #2e5bff"></span>报价数</span>
					<span><span class="legend-dot" style="background: #10b981"></span>中标数</span>
				</div>
			</div>
			<div class="chart-container">
				<div ref="chartRef" class="trend-chart"></div>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import { computed, ref, reactive, onMounted, watch } from 'vue';
import { storeToRefs } from 'pinia';
import { useDashboardStore } from '/@/stores/modules/dashboard';
import { useUserInfo } from '/@/stores/userInfo';
import * as echarts from 'echarts';
import HomeBg from '/@/assets/home-bg.png';
import * as api from '/@/views/system/personal/api';

// 定义消息类型
interface NewsItem {
	creator_name: string;
	create_datetime: string;
	title: string;
}

const store = useDashboardStore();
const { supplier } = storeToRefs(store);
const userInfo = useUserInfo();

const chartRef = ref();

const defaultNewsItems: NewsItem[] = [];

const newsInfoList = reactive<NewsItem[]>([...defaultNewsItems]);

// 快捷入口列表
const quickNavList = [
	{ icon: 'fa fa-user-o', label: '角色管理', iconColor: '#6B7280', bgColor: '#F3F4F6', url: '#/role' },
	{ icon: 'fa fa-sitemap', label: '部门管理', iconColor: '#6B7280', bgColor: '#F3F4F6', url: '#/dept' },
	{ icon: 'iconfont icon-system', label: '系统配置', iconColor: '#6B7280', bgColor: '#F3F4F6', url: '#/config' },
	{ icon: 'iconfont icon-dict', label: '字典管理', iconColor: '#6B7280', bgColor: '#F3F4F6', url: '#/dictionary' },
	{ icon: 'iconfont icon-Area', label: '区域管理', iconColor: '#6B7280', bgColor: '#F3F4F6', url: '#/areas' },
	{ icon: 'iconfont icon-xiaoxizhongxin', label: '消息中心', iconColor: '#6B7280', bgColor: '#F3F4F6', url: '#/messageCenter' },
];

function handleNavClick(url: string) {
	window.location.href = url;
}

const kpi = computed(
	() =>
		supplier.value?.kpi || {
			total_quotes: 0,
			pending_quotes: 0,
			won_quotes: 0,
			conversion_rate: 0,
		}
);
const pendingQuotes = computed(() => supplier.value?.pending_quotes || []);
const trend = computed(() => supplier.value?.trend || []);

// 获取消息列表
const getMsg = (): void => {
	// 先重置为默认数据
	newsInfoList.length = 0;
	newsInfoList.push(...defaultNewsItems);

	// 尝试从API获取最新数据
	api.GetSelfReceive({}).then((res: any) => {
		const { data } = res || {};
		// 严格检查返回数据的有效性
		if (data && Array.isArray(data) && data.length > 0) {
			try {
				// 安全地进行类型转换并更新状态
				newsInfoList.length = 0;
				newsInfoList.push(
					...data.map((item: any): NewsItem => ({
						creator_name: String(item.creator_name || '未知用户'),
						create_datetime: String(item.create_datetime || ''),
						title: String(item.title || ''),
					}))
				);
			} catch {
				// 类型转换失败时保持默认数据
			}
		}
	}).catch(() => {
		// 错误时保持已设置的默认数据
	});
};

function handleQuote(quote: any) {
	// TODO: navigate to quote page
}

function getQuoteStatusClass(status: number) {
	if (status === 1) return 'status-pending';
	if (status === 2) return 'status-quoting';
	if (status === 3) return 'status-normal';
	return 'status-normal';
}

function getQuoteStatusText(status: number) {
	if (status === 1) return '未报价';
	if (status === 2) return '报价中';
	if (status === 3) return '已报价';
	return '未报价';
}

function getMethodClass(method: string | undefined) {
	if (method === '招标') return 'method-tender';
	return 'method-inquiry';
}

function getMethodText(method: string | undefined) {
	return method || '询价';
}

function isTenderQuote(quote: any): boolean {
	return quote?.method === '招标';
}

function formatDateTimeYMDHM(iso: string | Date | null | undefined): string {
	if (!iso) return '-';
	const d = new Date(iso);
	if (Number.isNaN(d.getTime())) return '-';
	const y = d.getFullYear();
	const m = String(d.getMonth() + 1).padStart(2, '0');
	const day = String(d.getDate()).padStart(2, '0');
	const h = String(d.getHours()).padStart(2, '0');
	const min = String(d.getMinutes()).padStart(2, '0');
	return `${y}-${m}-${day} ${h}:${min}`;
}

function formatTimeHM(iso: string | Date): string {
	const d = new Date(iso);
	if (Number.isNaN(d.getTime())) return '-';
	const h = String(d.getHours()).padStart(2, '0');
	const min = String(d.getMinutes()).padStart(2, '0');
	return `${h}:${min}`;
}

function formatTenderBidTimeRange(
	start: string | Date | null | undefined,
	end: string | Date | null | undefined
): string {
	if (!start && !end) return '-';
	if (!start) return formatDateTimeYMDHM(end);
	if (!end) return formatDateTimeYMDHM(start);
	const s = new Date(start);
	const e = new Date(end);
	if (Number.isNaN(s.getTime()) || Number.isNaN(e.getTime())) return '-';
	const sameDay =
		s.getFullYear() === e.getFullYear() &&
		s.getMonth() === e.getMonth() &&
		s.getDate() === e.getDate();
	if (sameDay) {
		const y = s.getFullYear();
		const m = String(s.getMonth() + 1).padStart(2, '0');
		const day = String(s.getDate()).padStart(2, '0');
		return `${y}-${m}-${day} ${formatTimeHM(s)} 至 ${formatTimeHM(e)}`;
	}
	return `${formatDateTimeYMDHM(s)} 至 ${formatDateTimeYMDHM(e)}`;
}

function formatDurationCn(diffMs: number): string {
	if (diffMs <= 0) return '已到期';
	const totalHours = Math.floor(diffMs / (1000 * 60 * 60));
	const days = Math.floor(totalHours / 24);
	const hours = totalHours % 24;
	if (days > 0) return `${days}天${hours}小时`;
	return `${hours}小时`;
}

function getInquiryHoursToQuoteDeadline(quote: any): number | null {
	const q = quote?.quote_deadline;
	if (!q) return null;
	return (new Date(q).getTime() - Date.now()) / (1000 * 60 * 60);
}

function getDeadlinePrimaryLabel(quote: any): string {
	return isTenderQuote(quote) ? '投标时间：' : '报价截止时间：';
}

function getDeadlinePrimaryValue(quote: any): string {
	if (isTenderQuote(quote)) {
		return formatTenderBidTimeRange(quote?.bid_start_time, quote?.bid_end_time);
	}
	return formatDateTimeYMDHM(quote?.quote_deadline);
}

function getDeadlineRemainingValue(quote: any): string {
	if (isTenderQuote(quote)) {
		const start = quote?.bid_start_time;
		const end = quote?.bid_end_time;
		if (!start) return '-';
		const now = Date.now();
		const startMs = new Date(start).getTime();
		const endMs = end ? new Date(end).getTime() : null;
		if (now < startMs) return formatDurationCn(startMs - now);
		if (endMs != null && now < endMs) return '投标进行中';
		if (endMs != null && now >= endMs) return '已结束';
		return '已开始';
	}
	const q = quote?.quote_deadline;
	if (!q) return '-';
	return formatDurationCn(new Date(q).getTime() - Date.now());
}

function getDeadlineValueClass(quote: any): string {
	if (isTenderQuote(quote)) {
		return 'deadline-tender-accent';
	}
	const h = getInquiryHoursToQuoteDeadline(quote);
	if (h == null || quote?.quote_deadline == null) return '';
	if (h < 0) return 'deadline-expired';
	if (h < 24) return 'deadline-urgent';
	if (h < 48) return 'deadline-warning';
	return 'deadline-accent-normal';
}

function initChart() {
	if (!chartRef.value) return;
	const chart = echarts.getInstanceByDom(chartRef.value) || echarts.init(chartRef.value);

	// 使用后端返回的 trend 数据，如果没有则用模拟数据
	let labels: string[] = [];
	let quotesData: number[] = [];
	let wonData: number[] = [];

	if (trend.value && trend.value.length > 0) {
		// 生成当前月的所有日期，确保每天都能显示
		const now = new Date();
		const year = now.getFullYear();
		const month = now.getMonth();
		const daysInMonth = new Date(year, month + 1, 0).getDate();

		// 创建数据映射
		const quotesMap = new Map(trend.value.map((d) => [d.day, d.quotes || 0]));
		const wonMap = new Map(trend.value.map((d) => [d.day, d.won || 0]));

		// 填充所有日期，缺失的填0
		labels = [];
		quotesData = [];
		wonData = [];
		for (let day = 1; day <= daysInMonth; day++) {
			labels.push(`${month + 1}/${day}`);
			quotesData.push(quotesMap.get(day) || 0);
			wonData.push(wonMap.get(day) || 0);
		}
	} else {
		// 模拟数据
		const today = new Date();
		for (let i = 5; i >= 0; i--) {
			const d = new Date(today);
			d.setMonth(d.getMonth() - i);
			labels.push(`${d.getFullYear()}-${(d.getMonth() + 1).toString().padStart(2, '0')}`);
		}
		quotesData = [12, 15, 18, 14, 20, 22];
		wonData = [3, 5, 6, 4, 7, 8];
	}

	chart.setOption({
		tooltip: {
			trigger: 'axis',
			axisPointer: { type: 'cross' },
		},
		grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
		xAxis: {
			type: 'category',
			data: labels,
			boundaryGap: false,
			axisLine: { lineStyle: { color: '#E5E7EB' } },
			axisLabel: { color: '#9CA3AF', fontSize: 11 },
		},
		yAxis: [
			{
				type: 'value',
				name: '单据数量',
				min: 0,
				axisLine: { show: false },
				axisLabel: { color: '#9CA3AF', fontSize: 11 },
				splitLine: { lineStyle: { color: '#F3F4F6', type: 'dashed' } },
			},
		],
		series: [
			{
				name: '报价数',
				type: 'line',
				data: quotesData,
				smooth: true,
				itemStyle: { color: '#2E5BFF' },
				areaStyle: { color: 'rgba(46, 91, 255, 0.05)' },
				lineStyle: { width: 2 },
			},
			{
				name: '中标数',
				type: 'line',
				data: wonData,
				smooth: true,
				itemStyle: { color: '#10B981' },
				areaStyle: { color: 'rgba(16, 185, 129, 0.05)' },
				lineStyle: { width: 2 },
			},
		],
	});
}

onMounted(() => {
	initChart();
	getMsg();
	window.addEventListener('resize', () => chartRef.value && echarts.getInstanceByDom(chartRef.value)?.resize());
});

watch(trend, () => {
	initChart();
});
</script>

<style scoped lang="scss">
.supplier-dashboard {
	/* 欢迎语 */
	.welcome-header {
		margin-bottom: 24px;
		font-size: 16px;
		font-weight: 700;

		.welcome-text {
			color: #1f2937;
		}

		.welcome-sub {
			font-size: 12px;
			color: #9ca3af;
			margin-left: 8px;
		}
	}

	--primary-color: #2e5bff;
	--text-main: #1f2937;
	--text-secondary: #6b7280;
	--bg-body: #f3f4f6;
	--bg-card: #ffffff;
	--danger: #ef4444;
	--warning: #f59e0b;
	--success: #10b981;
	--gold: #d4af37;
	--border-color: #e5e7eb;
	font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
	background: var(--bg-body);
	padding: 24px;
	border-radius: 0;
	margin: -24px;
	min-height: calc(100vh - 64px);
}

/* KPI 卡片区域 */
.kpi-section {
	display: grid;
	grid-template-columns: repeat(4, 1fr);
	gap: 24px;
	margin-bottom: 24px;
}

.kpi-card {
	background: var(--bg-card);
	padding: 24px;
	border-radius: 12px;
	box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
	border: 1px solid var(--border-color);
	position: relative;
	overflow: hidden;
	transition: transform 0.2s, box-shadow 0.2s;
	text-align: center;

	&:hover {
		transform: translateY(-2px);
		box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
	}

	&.green .kpi-icon {
		color: var(--success);
	}
	&.orange .kpi-icon {
		color: var(--warning);
	}
	&.gold .kpi-icon {
		color: var(--gold);
	}
	&.blue .kpi-icon {
		color: var(--primary-color);
	}

	/* 底部说明与卡片主题一致（避免语义类与主题色错位） */
	&.green .kpi-trend.trend-up {
		color: var(--success);
	}
	&.orange .kpi-trend {
		color: var(--warning);
	}
	&.gold .kpi-trend {
		color: var(--gold);
	}
	&.blue .kpi-trend.trend-flat {
		color: var(--primary-color);
	}
}

.kpi-icon {
	font-size: 28px;
	margin-bottom: 12px;
	opacity: 0.9;

	i {
		color: inherit;
	}
}

.kpi-title {
	font-size: 18px;
	color: var(--text-secondary);
	font-weight: 500;
}

.kpi-value {
	font-size: 52px;
	font-weight: 700;
	color: var(--text-main);
	margin: 20px 0 16px 0;
	letter-spacing: -2px;
}

.kpi-trend {
	font-size: 12px;
	font-weight: 500;
	display: flex;
	align-items: center;
	gap: 4px;

	&.trend-up {
		color: var(--success);
	}
	&.trend-flat {
		color: var(--warning);
	}
	&.trend-down {
		color: var(--danger);
	}
}

/* 主体容器 */
.main-container {
	display: grid;
	grid-template-columns: 2fr 1fr;
	gap: 24px;
	margin-bottom: 24px;
	align-items: stretch;
}

.task-card {
	display: flex;
	flex-direction: column;
}

/* 卡片通用样式 */
.card {
	background: var(--bg-card);
	border-radius: 12px;
	padding: 24px;
	box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
	border: 1px solid var(--border-color);
}

.card-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 20px;
}

.card-title {
	font-size: 16px;
	font-weight: 600;
	color: var(--text-main);
	display: flex;
	align-items: center;
	gap: 8px;
}

.view-all {
	font-size: 13px;
	color: var(--primary-color);
	text-decoration: none;
	font-weight: 500;
	display: flex;
	align-items: center;
	gap: 4px;

	&:hover {
		gap: 8px;
	}
}

/* 待办任务表格 */
.task-table-container {
	overflow-x: auto;
	overflow-y: auto;
	flex: 1;
	min-height: 100px;
}

table {
	width: 100%;
	border-collapse: collapse;
	font-size: 14px;
}

th {
	text-align: left;
	padding: 12px 16px;
	background-color: #f9fafb;
	color: var(--text-secondary);
	font-weight: 600;
	font-size: 13px;
	border-bottom: 1px solid var(--border-color);
}

td {
	padding: 16px;
	border-bottom: 1px solid #f3f4f6;
	color: var(--text-main);
	vertical-align: middle;
}

tr:hover {
	background-color: #f9fafb;
}

tr:last-child td {
	border-bottom: none;
}

.action-btn {
	padding: 6px 16px;
	border-radius: 6px;
	border: none;
	cursor: pointer;
	font-size: 13px;
	font-weight: 500;
	transition: all 0.2s;
}

.btn-primary {
	background-color: var(--primary-color);
	color: white;
}
.btn-primary:hover {
	background-color: #1d4eff;
}

/* 报价清单卡片 */
.quote-card {
	display: flex;
	flex-direction: column;
}

.quote-list {
	display: flex;
	flex-direction: column;
	gap: 12px;
	flex: 1;
	overflow-y: auto;
	min-height: 100px;
}

.quote-item {
	border: 1px solid var(--border-color);
	border-radius: 8px;
	padding: 16px;
	transition: all 0.2s;

	&:hover {
		border-color: var(--primary-color);
		box-shadow: 0 2px 8px rgba(46, 91, 255, 0.1);
	}
}

.quote-row {
	display: flex;
	align-items: center;
	gap: 12px;
	margin-bottom: 12px;
}

.quote-no {
	font-weight: 600;
	color: var(--text-main);
	font-size: 14px;
}

.quote-status {
	padding: 2px 8px;
	border-radius: 4px;
	font-size: 12px;
	font-weight: 500;
}

.status-pending {
	background-color: #fff7ed;
	color: #f59e0b;
	border: 1px solid #fcd34d;
}

.status-quoting {
	background-color: #eff6ff;
	color: #2e5bff;
	border: 1px solid #93c5fd;
}

.status-normal {
	background-color: #f3f4f6;
	color: #6b7280;
	border: 1px solid #d1d5db;
}

/* 采购方式badge */
.method-badge {
	padding: 2px 8px;
	border-radius: 4px;
	font-size: 12px;
	font-weight: 500;
	display: inline-block;
}
.method-inquiry {
	background-color: #f0fdf4;
	color: #16a34a;
	border: 1px solid #bbf7d0;
}
.method-tender {
	background-color: #faf5ff;
	color: #9333ea;
	border: 1px solid #e9d5ff;
}

/* 截止时间 / 剩余时间（与采购端仪表盘一致） */
.quote-deadline-cell {
	margin-left: auto;
	min-width: 220px;
	max-width: 340px;
	padding: 6px 10px;
	background: #f9fafb;
	border-radius: 6px;
}
.deadline-inner {
	border-collapse: collapse;
	width: 100%;
	table-layout: auto;
}
.deadline-td-label {
	vertical-align: top;
	white-space: nowrap;
	font-size: 13px;
	color: var(--text-main);
	padding: 0 8px 4px 0;
	line-height: 1.45;
}
.deadline-td-value {
	vertical-align: top;
	font-size: 13px;
	line-height: 1.45;
	padding: 0 0 4px 0;
}
.deadline-td-gap {
	padding: 0;
	width: 0;
}
.deadline-td-remaining {
	vertical-align: top;
	font-size: 12px;
	line-height: 1.45;
	padding: 0;
}
.deadline-remaining-label {
	color: var(--text-secondary);
	font-weight: 400;
	margin-right: 2px;
}
.deadline-urgent {
	color: var(--danger) !important;
	font-weight: 700;
}
.deadline-warning {
	color: var(--warning) !important;
	font-weight: 700;
}
.deadline-expired {
	color: #9ca3af !important;
	font-weight: 500;
	text-decoration: line-through;
}
.deadline-accent-normal {
	color: #ea580c !important;
	font-weight: 600;
}
.deadline-tender-accent {
	color: #ea580c !important;
	font-weight: 600;
}

.quote-info-row {
	display: flex;
	gap: 24px;
	padding-left: 2px;
}

.quote-info-item {
	display: flex;
	gap: 8px;
	align-items: center;

	.label {
		font-size: 13px;
		color: var(--text-secondary);
	}

	.value {
		font-size: 13px;
		color: var(--text-main);
		font-weight: 500;

		&.is-urgent {
			color: var(--danger);
		}
	}
}

.empty-cell {
	text-align: center;
	color: var(--text-secondary);
	padding: 32px !important;
	flex: 1;
	display: flex;
	align-items: center;
	justify-content: center;
}

/* 消息通知 */
.notif-badge {
	position: absolute;
	top: -8px;
	right: -12px;
	background: var(--danger);
	color: white;
	font-size: 10px;
	padding: 2px 6px;
	border-radius: 10px;
	font-weight: bold;
}

.notification-list {
	list-style: none;
}

.notification-item {
	display: flex;
	gap: 16px;
	padding: 16px 0;
	border-bottom: 1px solid #f3f4f6;

	&:last-child {
		border-bottom: none;
		padding-bottom: 0;
	}

	&:first-child {
		padding-top: 0;
	}

	&:hover {
		background-color: #f9fafb;
		margin: 0 -16px;
		padding-left: 16px;
		padding-right: 16px;
		border-radius: 8px;
	}
}

.notif-icon {
	width: 40px;
	height: 40px;
	border-radius: 10px;
	display: flex;
	align-items: center;
	justify-content: center;
	flex-shrink: 0;
	font-size: 18px;
}

.icon-quote {
	background: #eff6ff;
	color: #2563eb;
}
.icon-win {
	background: #ecfdf5;
	color: #059669;
}
.icon-alert {
	background: #fffbeb;
	color: #d97706;
}

.notif-content {
	flex: 1;
}

.notif-header {
	display: flex;
	justify-content: space-between;
	align-items: flex-start;
	margin-bottom: 4px;
}

.notif-title {
	font-weight: 600;
	color: var(--text-main);
	font-size: 14px;
}

.notif-time {
	font-size: 12px;
	color: #9ca3af;
	white-space: nowrap;
}

.notif-desc {
	color: var(--text-secondary);
	font-size: 13px;
	line-height: 1.5;
	margin-bottom: 8px;
}

.notif-link {
	color: var(--primary-color);
	text-decoration: none;
	font-size: 13px;
	font-weight: 500;

	&:hover {
		text-decoration: underline;
	}
}

.empty-notif {
	text-align: center;
	color: var(--text-secondary);
	padding: 32px 0;
}

/* 图表区域 */
.chart-section {
	margin-top: 0;
}

/* 右侧边栏 */
.right-sidebar {
	display: flex;
	flex-direction: column;
	gap: 24px;
	align-items: stretch;
}

.right-sidebar .card {
	flex: 1;
}

/* 图片卡片 */
.home-img-card {
	padding: 0;
	overflow: hidden;
	height: 200px;
}

.home-bg-img {
	width: 100%;
	height: 100%;
	object-fit: cover;
	display: block;
}

/* 图片+通知合并卡片 */
.img-notify-card {
	padding: 0;
	overflow: hidden;
	display: flex;
	flex-direction: column;
}

.img-notify-img {
	width: 100%;
	height: 180px;
	overflow: hidden;
	flex-shrink: 0;
}

.img-notify-img .home-bg-img {
	width: 100%;
	height: 100%;
	object-fit: cover;
}

.img-notify-list {
	flex: 1;
	padding: 16px;
	overflow-y: auto;
}

.notify-item {
	display: flex;
	gap: 10px;
	padding: 8px 0;
	border-bottom: 1px solid #f3f4f6;

	&:last-child {
		border-bottom: none;
	}
}

.notify-icon {
	width: 32px;
	height: 32px;
	border-radius: 8px;
	background: #f8f8f8;
	display: flex;
	align-items: center;
	justify-content: center;
	flex-shrink: 0;
}

.notify-content {
	flex: 1;
	min-width: 0;
}

.notify-title-row {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 2px;
}

.notify-title {
	font-size: 12px;
	font-weight: 500;
	color: var(--text-main);
}

.notify-time {
	font-size: 11px;
	color: #9ca3af;
	font-style: italic;
}

.notify-title-text {
	font-size: 12px;
	color: var(--text-secondary);
	white-space: nowrap;
	overflow: hidden;
	text-overflow: ellipsis;
}

/* 快捷入口 */
.quick-nav-grid {
	display: grid;
	grid-template-columns: repeat(2, 1fr);
	gap: 16px;
}

.quick-nav-item {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 6px;
	padding: 12px 8px;
	background: var(--bg-body);
	border-radius: 10px;
	cursor: pointer;
	transition: all 0.2s;

	&:hover {
		background: #e8eefe;
		transform: translateY(-2px);
	}
}

.quick-nav-icon {
	width: 36px;
	height: 36px;
	border-radius: 10px;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 16px;
}

.quick-nav-label {
	font-size: 13px;
	color: var(--text-main);
	font-weight: 500;
	text-align: center;
}

.chart-legend {
	font-size: 12px;
	color: var(--text-secondary);
	display: flex;
	gap: 16px;

	span {
		display: flex;
		align-items: center;
		gap: 6px;
	}
}

.legend-dot {
	width: 8px;
	height: 8px;
	border-radius: 50%;
}

.chart-container {
	position: relative;
	height: 300px;
}

.trend-chart {
	width: 100%;
	height: 100%;
}

/* 响应式 */
@media (max-width: 1200px) {
	.main-container {
		grid-template-columns: 1fr;
	}
	.right-sidebar {
		flex-direction: row;
	}
	.home-img-card {
		flex: 1;
		height: auto;
	}
	.quick-nav-card {
		flex: 1;
	}
	.kpi-section {
		grid-template-columns: repeat(2, 1fr);
	}
}

@media (max-width: 768px) {
	.kpi-section {
		grid-template-columns: 1fr;
	}
	.right-sidebar {
		flex-direction: column;
	}
	.home-img-card {
		height: 180px;
	}
	.quick-nav-grid {
		grid-template-columns: repeat(3, 1fr);
	}
}
</style>
