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
				<el-tag style="margin-right: 20px">{{ RoleDrawer.roleName }}</el-tag>
				授权人员：
				<el-button size="small" :icon="UserFilled" @click="handleUsers">{{ RoleDrawer.users.length }}</el-button>
			</div>
		</template>
		<splitpanes class="default-theme" style="height: 100%">
			<pane min-size="20" size="22">
				<div class="pane-box">
					<MenuTreeCom />
				</div>
			</pane>
			<pane min-size="20">
				<div class="pane-box">
					<el-tabs v-model="activeName" class="demo-tabs">
						<el-tab-pane label="接口权限" name="first"><MenuBtnCom /></el-tab-pane>
						<el-tab-pane label="列字段权限" name="second"><MenuFieldCom /></el-tab-pane>
					</el-tabs>
				</div>
			</pane>
		</splitpanes>
	</el-drawer>

	<el-dialog v-model="dialogVisible" title="授权用户" width="700px" :close-on-click-modal="false">
		<RoleUsersCom />
	</el-dialog>
</template>

<script setup lang="ts">
import { Splitpanes, Pane } from 'splitpanes';
import 'splitpanes/dist/splitpanes.css';
import { UserFilled } from '@element-plus/icons-vue';
import { RoleDrawerStores } from '../stores/RoleDrawerStores';
import { defineAsyncComponent, ref } from 'vue';
import { RoleUsersStores } from '../stores/RoleUsersStores';

const MenuTreeCom = defineAsyncComponent(() => import('./RoleMenuTree.vue'));
const MenuBtnCom = defineAsyncComponent(() => import('./RoleMenuBtn.vue'));
const MenuFieldCom = defineAsyncComponent(() => import('./RoleMenuField.vue'));
const RoleUsersCom = defineAsyncComponent(() => import('./RoleUsers.vue'));
const RoleDrawer = RoleDrawerStores(); // 抽屉参数
const RoleUsers = RoleUsersStores(); // 角色-用户
const activeName = ref('first');

const dialogVisible = ref(false);

const handleUsers = () => {
	dialogVisible.value = true;
	RoleUsers.get_all_users(); // 获取所有用户
	RoleUsers.set_right_users(RoleDrawer.$state.users); // 设置已选中用户
};
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
