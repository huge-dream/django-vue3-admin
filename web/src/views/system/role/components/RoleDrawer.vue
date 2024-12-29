<template>
	<el-drawer
		v-model="RoleDrawer.drawerVisible"
		title="权限配置"
		direction="rtl"
		size="80%"
		:close-on-click-modal="false"
		:before-close="RoleDrawer.handleDrawerClose"
		:destroy-on-close="true"
	>
		<template #header>
			<div>
				当前授权角色：
				<el-tag>{{ RoleDrawer.roleName }}</el-tag>
			</div>
		</template>
		<splitpanes class="default-theme" style="height: 100%">
			<pane min-size="20" size="22">
				<div class="pane-box">
					<MenuTree />
				</div>
			</pane>
			<pane min-size="20">
				<div class="pane-box">
					<el-tabs v-model="activeName" class="demo-tabs">
						<el-tab-pane label="接口权限" name="first"><MenuBtn /></el-tab-pane>
						<el-tab-pane label="列字段权限" name="second"><MenuField /></el-tab-pane>
					</el-tabs>
				</div>
			</pane>
		</splitpanes>
	</el-drawer>
</template>

<script setup lang="ts">
import { Splitpanes, Pane } from 'splitpanes';
import 'splitpanes/dist/splitpanes.css';
import { RoleDrawerStores } from '../stores/RoleDrawerStores';
import { defineAsyncComponent, ref } from 'vue';

const MenuTree = defineAsyncComponent(() => import('./RoleMenuTree.vue'));
const MenuBtn = defineAsyncComponent(() => import('./RoleMenuBtn.vue'));
const MenuField = defineAsyncComponent(() => import('./RoleMenuField.vue'));
const RoleDrawer = RoleDrawerStores(); // 抽屉参数
const activeName = ref('first');
</script>

<style lang="scss" scoped>
.pane-box {
	width: 100vw; /* 视口宽度 */
	height: 100vh; /* 视口高度 */
	max-width: 100%; /* 确保不超过父元素的宽度 */
	max-height: 100%; /* 确保不超过父元素的高度 */
	overflow: auto; /* 当内容超出容器尺寸时显示滚动条 */
	padding: 10px;
	background-color: #fff;
}
</style>
