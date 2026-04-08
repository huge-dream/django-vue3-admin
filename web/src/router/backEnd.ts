import { RouteRecordRaw } from 'vue-router';

/** 供应商报价详情（隐藏菜单）。仅带 `?mode=edit` 为编辑，否则默认查看（含仅点标签页进入）。 */
const pissupplierQuotationDetailRoute: RouteRecordRaw = {
	path: '/pissupplier/quotation/detail/:id',
	name: 'PissupplierQuotationDetail',
	component: () => import('/@/views/pissupplier/quotation/detail.vue'),
	meta: {
		title: '报价单详情',
		isLink: '',
		isHide: true,
		isKeepAlive: false,
		isAffix: false,
		isIframe: false,
		roles: ['admin'],
		icon: ''
	}
};

/** 采购端杂采询价单详情（隐藏菜单）。`id=new` 且 `mode=create` 为新建；否则 `id` 为数字主键，`mode=edit|view`。 */
const pisadminRfqMiscInquiryDetailRoute: RouteRecordRaw = {
	path: '/pisadmin/miscprocurement/rfqmiscellaneous/miscInquiryDetail/:id',
	name: 'PisadminRfqMiscInquiryDetail',
	component: () => import('/@/views/pisadmin/miscprocurement/rfqmiscellaneous/miscInquiryDetail.vue'),
	meta: {
		title: '询价单详情',
		isLink: '',
		isHide: true,
		isKeepAlive: false,
		isAffix: false,
		isIframe: false,
		roles: ['admin'],
		icon: ''
	}
};

/** 杂采比价/议价（隐藏菜单）。`id` 为询价单主键。 */
const pisadminRfqMiscComparePriceRoute: RouteRecordRaw = {
	path: '/pisadmin/miscprocurement/rfqmiscellaneous/comparePrice/:id',
	name: 'PisadminRfqMiscComparePrice',
	component: () => import('/@/views/pisadmin/miscprocurement/rfqmiscellaneous/comparePrice.vue'),
	meta: {
		title: '比价/议价',
		isLink: '',
		isHide: true,
		isKeepAlive: false,
		isAffix: false,
		isIframe: false,
		roles: ['admin'],
		icon: ''
	}
};

/** 杂采材料管理（隐藏菜单，供比价页链入；菜单中若已配置同页可并存）。 */
const pisadminMiscMaterialsIndexRoute: RouteRecordRaw = {
	path: '/pisadmin/miscprocurement/misc_materials/index',
	name: 'PisadminMiscMaterialsIndex',
	component: () => import('/@/views/pisadmin/miscprocurement/misc_materials/index.vue'),
	meta: {
		title: '杂采材料管理',
		isLink: '',
		isHide: true,
		isKeepAlive: false,
		isAffix: false,
		isIframe: false,
		roles: ['admin'],
		icon: ''
	}
};

/** 询价单操作日志（隐藏菜单；与菜单中配置的同名页可并存）。 */
const pisadminRfsOperationLogsRoute: RouteRecordRaw = {
	path: '/pisadmin/miscprocurement/rfs_operation_logs/index',
	name: 'PisadminRfsOperationLogs',
	component: () => import('/@/views/pisadmin/miscprocurement/rfs_operation_logs/index.vue'),
	meta: {
		title: '询价单操作日志',
		isLink: '',
		isHide: true,
		isKeepAlive: false,
		isAffix: false,
		isIframe: false,
		roles: ['admin'],
		icon: ''
	}
};
import { storeToRefs } from 'pinia';
import pinia from '/@/stores/index';
import { useUserInfo } from '/@/stores/userInfo';
import { useRequestOldRoutes } from '/@/stores/requestOldRoutes';
import { Session } from '/@/utils/storage';
import { NextLoading } from '/@/utils/loading';
import { dynamicRoutes, notFoundAndNoPower } from '/@/router/route';
import { formatTwoStageRoutes, formatFlatteningRoutes, router } from '/@/router/index';
import { useRoutesList } from '/@/stores/routesList';
import { useTagsViewRoutes } from '/@/stores/tagsViewRoutes';
import { useMenuApi } from '/@/api/menu/index';
import { handleMenu } from '../utils/menu';
import { BtnPermissionStore } from '/@/plugin/permission/store.permission';
import {SystemConfigStore} from "/@/stores/systemConfig";
import {useDeptInfoStore} from "/@/stores/modules/dept";
import {DictionaryStore} from "/@/stores/dictionary";
import {useFrontendMenuStore} from "/@/stores/frontendMenu";
import {useThemeConfig} from "/@/stores/themeConfig";
import {toRaw} from "vue";
import mitt from "/@/utils/mitt";
const menuApi = useMenuApi();

const layouModules: any = import.meta.glob('../layout/routerView/*.{vue,tsx}');
const viewsModules: any = import.meta.glob('../views/**/*.{vue,tsx}');
const greatDream: any = import.meta.glob('@great-dream/**/*.{vue,tsx}');

/**
 * 获取目录下的 .vue、.tsx 全部文件
 * @method import.meta.glob
 * @link 参考：https://cn.vitejs.dev/guide/features.html#json
 */
const dynamicViewsModules: Record<string, Function> = Object.assign({}, { ...layouModules }, { ...viewsModules }, { ...greatDream });

/**
 * 后端控制路由：初始化方法，防止刷新时路由丢失
 * @method NextLoading 界面 loading 动画开始执行
 * @method useUserInfo().setUserInfos() 触发初始化用户信息 pinia
 * @method useRequestOldRoutes().setRequestOldRoutes() 存储接口原始路由（未处理component），根据需求选择使用
 * @method setAddRoute 添加动态路由
 * @method setFilterMenuAndCacheTagsViewRoutes 设置路由到 vuex routesList 中（已处理成多级嵌套路由）及缓存多级嵌套数组处理后的一维数组
 */
export async function initBackEndControlRoutes() {
	// 界面 loading 动画开始执行
	if (window.nextLoading === undefined) NextLoading.start();
	// 无 token 停止执行下一步
	const token = Session.get('token');
	if (!token) {
		return false;
	}
	// 触发初始化用户信息 pinia
	// https://gitee.com/lyt-top/vue-next-admin/issues/I5F1HP
	await useUserInfo().getApiUserInfo();
	// 获取路由菜单数据
	const res = await getBackEndControlRoutes();
	// 无登录权限时，添加判断
	// https://gitee.com/lyt-top/vue-next-admin/issues/I64HVO
	// if (res.data.length <= 0) return Promise.resolve(true);
	// 处理路由（component），替换 dynamicRoutes（/@/router/route）第一个顶级 children 的路由
	const {frameIn,frameOut} = handleMenu(res.data)
	const frameInProcessed = await backEndComponent(frameIn)
	dynamicRoutes[0].children = [
		...(frameInProcessed || []),
		pissupplierQuotationDetailRoute,
		pisadminRfqMiscInquiryDetailRoute,
		pisadminRfqMiscComparePriceRoute,
		pisadminMiscMaterialsIndexRoute,
		pisadminRfsOperationLogsRoute
	]
	// 添加动态路由
	await setAddRoute();
	// 设置路由到 vuex routesList 中（已处理成多级嵌套路由）及缓存多级嵌套数组处理后的一维数组
	await setFilterMenuAndCacheTagsViewRoutes();
}

export async function setRouters(){
	const {frameInRoutes,frameOutRoutes} = await useFrontendMenuStore().getRouter()
	const frameInRouter = toRaw(frameInRoutes)
	const frameOutRouter = toRaw(frameOutRoutes)
	dynamicRoutes[0].children = [
		...frameInRouter,
		pissupplierQuotationDetailRoute,
		pisadminRfqMiscInquiryDetailRoute,
		pisadminRfqMiscComparePriceRoute,
		pisadminMiscMaterialsIndexRoute,
		pisadminRfsOperationLogsRoute
	]
	dynamicRoutes.forEach((item:any)=>{
		router.addRoute(item)
	})
	frameOutRouter.forEach((item:any)=>{
		router.addRoute(item)
	})
	const storesRoutesList = useRoutesList(pinia);
	storesRoutesList.setRoutesList([...dynamicRoutes[0].children,...frameOutRouter]);
	const storesTagsView = useTagsViewRoutes(pinia);
	storesTagsView.setTagsViewRoutes([...dynamicRoutes[0].children,...frameOutRouter])

}

/**
 * 设置路由到 vuex routesList 中（已处理成多级嵌套路由）及缓存多级嵌套数组处理后的一维数组
 * @description 用于左侧菜单、横向菜单的显示
 * @description 用于 tagsView、菜单搜索中：未过滤隐藏的(isHide)
 */
export function setFilterMenuAndCacheTagsViewRoutes() {
	const storesRoutesList = useRoutesList(pinia);
	storesRoutesList.setRoutesList(dynamicRoutes[0].children as any);
	setCacheTagsViewRoutes();
}

/**
 * 缓存多级嵌套数组处理后的一维数组
 * @description 用于 tagsView、菜单搜索中：未过滤隐藏的(isHide)
 */
export function setCacheTagsViewRoutes() {
	const storesTagsView = useTagsViewRoutes(pinia);
	storesTagsView.setTagsViewRoutes(formatTwoStageRoutes(formatFlatteningRoutes(dynamicRoutes))[0].children);
}

/**
 * 处理路由格式及添加捕获所有路由或 404 Not found 路由
 * @description 替换 dynamicRoutes（/@/router/route）第一个顶级 children 的路由
 * @returns 返回替换后的路由数组
 */
export function setFilterRouteEnd() {
	let filterRouteEnd: any = formatTwoStageRoutes(formatFlatteningRoutes(dynamicRoutes));
	// notFoundAndNoPower 防止 404、401 不在 layout 布局中，不设置的话，404、401 界面将全屏显示
	// 关联问题 No match found for location with path 'xxx'
	filterRouteEnd[0].children = [...filterRouteEnd[0].children, ...notFoundAndNoPower];
	return filterRouteEnd;
}

/**
 * 添加动态路由
 * @method router.addRoute
 * @description 此处循环为 dynamicRoutes（/@/router/route）第一个顶级 children 的路由一维数组，非多级嵌套
 * @link 参考：https://next.router.vuejs.org/zh/api/#addroute
 */
export async function setAddRoute() {
	await setFilterRouteEnd().forEach((route: RouteRecordRaw) => {
		router.addRoute(route);
	});
}

/**
 * 请求后端路由菜单接口
 * @description isRequestRoutes 为 true，则开启后端控制路由
 * @returns 返回后端路由菜单数据
 */
export function getBackEndControlRoutes() {
	//获取所有的按钮权限
	BtnPermissionStore().getBtnPermissionStore();
	// 获取系统配置
	SystemConfigStore().getSystemConfigs()
	// 获取所有部门信息
	useDeptInfoStore().requestDeptInfo()
	// 获取字典信息
	DictionaryStore().getSystemDictionarys()
	const { themeConfig } = storeToRefs(useThemeConfig(pinia))
	return menuApi.getSystemMenu({ language: themeConfig.value.globalI18n });
}

/**
 * 根据语言重新请求后端路由菜单
 * @description 用于语言切换后刷新路由
 */
export async function refreshRoutesForI18n() {
	const { themeConfig } = storeToRefs(useThemeConfig(pinia));
	const res = await menuApi.getSystemMenu({ language: themeConfig.value.globalI18n });
	const { frameIn, frameOut } = handleMenu(res.data);
	const frameInProcessed = await backEndComponent(frameIn);
	dynamicRoutes[0].children = [
		...(frameInProcessed || []),
		pissupplierQuotationDetailRoute,
		pisadminRfqMiscInquiryDetailRoute,
		pisadminRfqMiscComparePriceRoute,
		pisadminMiscMaterialsIndexRoute,
		pisadminRfsOperationLogsRoute
	];
	const storesRoutesList = useRoutesList(pinia);
	storesRoutesList.setRoutesList([...(dynamicRoutes[0].children || []), ...frameOut]);
	// 通知侧边栏刷新菜单
	mitt.emit('getBreadcrumbIndexSetFilterRoutes');
}

/**
 * 重新请求后端路由菜单接口
 * @description 用于菜单管理界面刷新菜单（未进行测试）
 * @description 路径：/src/views/system/menu/component/addMenu.vue
 */
export function setBackEndControlRefreshRoutes() {
	getBackEndControlRoutes();
}

/**
 * 后端路由 component 转换
 * @param routes 后端返回的路由表数组
 * @returns 返回处理成函数后的 component
 */
export function backEndComponent(routes: any) {
	if (!routes) return;
	return routes.map((item: any) => {
		if (item.component) item.component = dynamicImport(dynamicViewsModules, item.component as string);
		if(item.is_catalog){
			// 对目录的处理
			item.component = dynamicImport(dynamicViewsModules, 'layout/routerView/parent')
		}
		if(item.is_link){
			// 对外链接的处理
			if(item.is_iframe){
				item.component = dynamicImport(dynamicViewsModules, 'layout/routerView/iframes')
			}else {
				item.component = dynamicImport(dynamicViewsModules, 'layout/routerView/link')
			}
		}else{
			if(item.is_iframe){
				// const iframeRoute:RouteRecordRaw = {
				// 	...item
				// }
				// router.addRoute(iframeRoute)
				item.meta.isLink = item.link_url
				// item.path = `${item.path}Link`
				// item.name = `${item.name}Link`
				// item.meta.isIframe = item.is_iframe
				// item.meta.isKeepAlive = false
				// item.meta.isIframeOpen = true
				item.component = dynamicImport(dynamicViewsModules, 'layout/routerView/link.vue')
			}
		}
		item.children && backEndComponent(item.children);
		return item;
	});
}

/**
 * 后端路由 component 转换函数
 * @param dynamicViewsModules 获取目录下的 .vue、.tsx 全部文件
 * @param component 当前要处理项 component
 * @returns 返回处理成函数后的 component
 */
export function dynamicImport(dynamicViewsModules: Record<string, Function>, component: string) {
	const keys = Object.keys(dynamicViewsModules);
	const matchKeys = keys.filter((key) => {
		const k = key.replace(/..\/views|../, '');
		const k0 = k.replace("ode_modules/@great-dream/", '')
		const k1 = k0.replace("/plugins", '')
		const newComponent = component.replace("plugins/", "")
		return k1.startsWith(`${newComponent}`) || k1.startsWith(`/${newComponent}`);
	});
	if (matchKeys?.length === 1) {
		const matchKey = matchKeys[0];
		return dynamicViewsModules[matchKey];
	}
	if (matchKeys?.length > 1) {
		return false;
	}
}
