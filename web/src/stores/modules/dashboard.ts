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
		method?: string;
		quote_deadline?: string | null;
		bid_start_time?: string | null;
		bid_end_time?: string | null;
	}>;
	messages: Array<{
		id: number;
		title: string;
		content: string;
		is_read: boolean;
		created_at: string;
	}>;
	trend: Array<{ month?: string; day?: number; count: number }>;
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
		quantity: string | number;
		unit: string;
		status: number;
		method?: string;
		quote_deadline?: string | null;
		bid_start_time?: string | null;
		bid_end_time?: string | null;
	}>;
	messages: Array<{
		id: number;
		title: string;
		content: string;
		is_read: boolean;
		created_at: string;
	}>;
	trend: Array<{ month?: string; day?: number; quotes?: number; won?: number }>;
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
				console.log('[Dashboard Store] API response:', res);
				// 后端返回 {code: 200, msg, data: {buyer, supplier}}，需要取 res.data
				const data = res?.data || res;
				console.log('[Dashboard Store] buyer data:', data?.buyer);
				console.log('[Dashboard Store] supplier data:', data?.supplier);
				console.log('[Dashboard Store] buyer.tasks:', data?.buyer?.tasks);
				console.log('[Dashboard Store] supplier.pending_quotes:', data?.supplier?.pending_quotes);
				this.buyer = data?.buyer || null;
				this.supplier = data?.supplier || null;
				console.log('[Dashboard Store] store.buyer after set:', this.buyer);
				console.log('[Dashboard Store] store.supplier after set:', this.supplier);
			} finally {
				this.loading = false;
			}
		},
	},
});
