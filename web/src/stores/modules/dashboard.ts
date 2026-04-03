import { defineStore } from 'pinia';
import { getDashboard } from '/@/api/pisadmin/dashboard';

interface BuyerDashboard {
	kpi: {
		total_inquiries: number;
		pending_inquiries: number;
		completed_quotes: number;
		total_suppliers: number;
		quote_timely_rate: number;
	} | null;
	tasks: Array<{
		id: number;
		title: string;
		inquiry_no: string;
		status: string;
		created_at: string;
	}>;
	messages: Array<{
		id: number;
		title: string;
		content: string;
		is_read: boolean;
		created_at: string;
	}>;
	trend: Array<{ month: string; count: number }>;
}

interface SupplierDashboard {
	kpi: {
		total_quotes: number;
		pending_quotes: number;
		won_quotes: number;
		conversion_rate: number;
	} | null;
	pending_quotes: Array<{
		id: number;
		inquiry_no: string;
		item_name: string;
		quantity: number;
		unit: string;
		deadline: string;
		status: number;
	}>;
	messages: Array<{
		id: number;
		title: string;
		content: string;
		is_read: boolean;
		created_at: string;
	}>;
	trend: Array<{ month: string; quotes: number; won: number }>;
}

export const useDashboardStore = defineStore('dashboard', {
	state: () => ({
		buyer: null as BuyerDashboard | null,
		supplier: null as SupplierDashboard | null,
		loading: false,
	}),
	actions: {
		async fetchDashboard() {
			this.loading = true;
			try {
				const res: any = await getDashboard();
				// 后端直接返回 {buyer, supplier} 结构
				this.buyer = res?.buyer || null;
				this.supplier = res?.supplier || null;
			} finally {
				this.loading = false;
			}
		},
	},
});
