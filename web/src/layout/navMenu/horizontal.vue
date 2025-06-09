<template>
	<div class="el-menu-horizontal-warp">
<!--		<el-scrollbar @wheel.native.prevent="onElMenuHorizontalScroll" ref="elMenuHorizontalScrollRef">-->
			<el-menu :default-active="defaultActive"  background-color="transparent" mode="horizontal">
				<template v-for="(val,index) in menuLists">
					<el-sub-menu :index="val.path" v-if="val.children && val.children.length > 0" :key="val.path">
						<template #title>
							<SvgIcon :name="val.meta.icon" />
							<span>{{ $t(val.meta.title) }}</span>
						</template>
						<SubItem :chil="val.children" />
					</el-sub-menu>
					<template v-else>
						<el-menu-item :index="val.path" :key="val.path" style="--el-menu-active-color: #fff" @click="onToRouteClick(val,index)">
							<template #title v-if="!val.meta.isLink || (val.meta.isLink && val.meta.isIframe)">
								<SvgIcon :name="val.meta.icon" />
								{{ $t(val.meta.title) }}
							</template>
							<template #title v-else>
								<a class="w100" @click.prevent="onALinkClick(val)">
									<SvgIcon :name="val.meta.icon" />
									{{ $t(val.meta.title) }}
								</a>
							</template>
						</el-menu-item>
					</template>
				</template>
			</el-menu>
<!--		</el-scrollbar>-->
	</div>
</template>

<script setup lang="ts" name="navMenuHorizontal">
import { defineAsyncComponent, reactive, computed, onMounted, nextTick, onBeforeMount, ref } from 'vue';
import {useRoute, onBeforeRouteUpdate, RouteRecordRaw, useRouter} from 'vue-router';
import { storeToRefs } from 'pinia';
import { useRoutesList } from '/@/stores/routesList';
import { useThemeConfig } from '/@/stores/themeConfig';
import other from '/@/utils/other';
import mittBus from '/@/utils/mitt';
const router = useRouter()
// 引入组件
const SubItem = defineAsyncComponent(() => import('/@/layout/navMenu/subItem.vue'));
const state = reactive<AsideState>({
	menuList: [],
  clientWidth: 0
});
// 定义父组件传过来的值
const props = defineProps({
	// 菜单列表
	menuList: {
		type: Array<RouteRecordRaw>,
		default: () => [],
	},
});

// 定义变量内容
const elMenuHorizontalScrollRef = ref();
const stores = useRoutesList();
const storesThemeConfig = useThemeConfig();
const { routesList } = storeToRefs(stores);
const { themeConfig } = storeToRefs(storesThemeConfig);
const route = useRoute();
const defaultActive = ref('')
// 获取父级菜单数据
const menuLists = computed(() => {
  <RouteItems>props.menuList.shift()
	return <RouteItems>props.menuList;
});
// 递归获取当前路由的顶级索引
const findFirstLevelIndex = (data, path) => {
	for (let index = 0; index < data.length; index++) {
		const item = data[index];
    // 检查当前菜单项是否有子菜单，并查找是否在子菜单中找到路径
		if (item.children && item.children.length > 0) {
			// 检查子菜单中是否有匹配的路径
			const childIndex = item.children.findIndex((child) => child.path === path);
			if (childIndex !== -1) {
				return index; // 返回当前一级菜单的索引
			}
			// 递归查找子菜单
			const foundIndex = findFirstLevelIndex(item.children, path);
			if (foundIndex !== null) {
				return index; // 返回找到的索引
			}
		}
	}
	return null; // 找不到路径时返回 null
};

// 初始化数据，页面刷新时，滚动条滚动到对应位置
const initElMenuOffsetLeft = () => {
	nextTick(() => {
		let els = <HTMLElement>document.querySelector('.el-menu.el-menu--horizontal li.is-active');
		if (!els) return false;
		// elMenuHorizontalScrollRef.value.$refs.wrapRef.scrollLeft = els.offsetLeft;
	});
};
// 路由过滤递归函数
const filterRoutesFun = <T extends RouteItem>(arr: T[]): T[] => {
	return arr
		.filter((item: T) => !item.meta?.isHide)
		.map((item: T) => {
			item = Object.assign({}, item);
			if (item.children) item.children = filterRoutesFun(item.children);
			return item;
		});
};
// 传送当前子级数据到菜单中
const setSendClassicChildren = (path: string) => {
	const currentPathSplit = path.split('/');
	let currentData: MittMenu = { children: [] };
	filterRoutesFun(routesList.value).map((v, k) => {
		if (v.path === `/${currentPathSplit[1]}`) {
			v['k'] = k;
			currentData['item'] = { ...v };
			currentData['children'] = [{ ...v }];
			if (v.children) currentData['children'] = v.children;
		}
	});
	return currentData;
};
// 设置页面当前路由高亮
const setCurrentRouterHighlight = (currentRoute: RouteToFrom) => {
	const { path, meta } = currentRoute;
	if (themeConfig.value.layout === 'classic') {
    let firstLevelIndex = (findFirstLevelIndex(routesList.value, route.path) || 0) - 1
    defaultActive.value = firstLevelIndex < 0 ? defaultActive.value : menuLists.value[firstLevelIndex].path
	} else {
		const pathSplit = meta?.isDynamic ? meta.isDynamicPath!.split('/') : path!.split('/');
		if (pathSplit.length >= 4 && meta?.isHide) defaultActive.value = pathSplit.splice(0, 3).join('/');
		else defaultActive.value = path;
	}
};
// 打开外部链接
const onALinkClick = (val: RouteItem) => {
	other.handleOpenLink(val);
};
// 跳转页面
const onToRouteClick = (val: RouteItem,index) => {
  // 跳转到子级页面
   let children = val.children
  if (children === undefined){
    defaultActive.value = val.path
    children = setSendClassicChildren(val.path).children
  }
  if (children.length >= 1){
    if (children[0].is_catalog) {
      onToRouteClick(children[0],index)
      return
    }
    router.push(children[0].path)
    let { layout, isClassicSplitMenu } = themeConfig.value;
    if (layout === 'classic' && isClassicSplitMenu) {
      mittBus.emit('setSendClassicChildren', children[0]);
    }
  } else {
    router.push('/home')
  }
};

// 页面加载前
onBeforeMount(() => {
	setCurrentRouterHighlight(route);
});
// 页面加载时
onMounted(() => {
	initElMenuOffsetLeft();
});
</script>

<style scoped lang="scss">
.el-menu-horizontal-warp {
	flex: 1;
	overflow: hidden;
	margin-right: 30px;
	:deep(.el-scrollbar__bar.is-vertical) {
		display: none;
	}
	:deep(a) {
		width: 100%;
	}
	.el-menu.el-menu--horizontal {
		display: flex;
		height: 100%;
		width: 100%;
		box-sizing: border-box;
	}
}
</style>
