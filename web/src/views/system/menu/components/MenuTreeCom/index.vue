<template>
	<el-input v-model="filterVal" :prefix-icon="Search" placeholder="请输入菜单名称" />
	<div class="menu-tree-com">
		<div class="mtc-head">
			<el-icon size="16" color="#606266" class="mtc-head-icon">
				<Menu />
			</el-icon>
			菜单列表
			<el-tooltip
				effect="dark"
				placement="right"
				content="1.红色菜单代表状态禁用; 2.添加菜单，如果是目录，组件地址为空即可; 3.添加根节点菜单，父级ID为空即可; 4.支持拖拽菜单;"
			>
				<el-icon size="16" color="var(--el-color-primary)" class="mtc-tooltip">
					<QuestionFilled />
				</el-icon>
			</el-tooltip>
		</div>

		<el-tree
			ref="treeRef"
			:data="treeData"
			:props="defaultTreeProps"
			:filter-node-method="filterNode"
			:load="handleTreeLoad"
			lazy
			:indent="45"
			@node-click="handleNodeClick"
			highlight-current
		>
			<template #default="{ node, data }">
				<element-tree-line :node="node" :showLabelLine="false" :indent="32">
					<span v-if="data.status" class="text-center font-black font-normal">
						<SvgIcon :name="node.data.icon" color="var(--el-color-primary)" />
						&nbsp;{{ node.label }}
					</span>
					<span v-else class="text-center font-black text-red-700 font-normal"> <SvgIcon :name="node.data.icon" />&nbsp;{{ node.label }} </span>
				</element-tree-line>
			</template>
		</el-tree>

		<div class="mtc-tags">
			<el-tooltip effect="dark" content="新增">
				<el-icon size="16" v-auth="'menu:Create'" @click="handleUpdateMenu('create')" class="mtc-tags-icon">
					<Plus />
				</el-icon>
			</el-tooltip>

			<el-tooltip effect="dark" content="编辑">
				<el-icon size="16" v-auth="'menu:Update'" @click="handleUpdateMenu('update')" class="mtc-tags-icon">
					<Edit />
				</el-icon>
			</el-tooltip>

			<el-tooltip effect="dark" content="上移">
				<el-icon size="16" v-auth="'menu:MoveUp'" @click="handleSort('up')" class="mtc-tags-icon">
					<Top />
				</el-icon>
			</el-tooltip>

			<el-tooltip effect="dark" content="下移">
				<el-icon size="16" v-auth="'menu:MoveDown'" @click="handleSort('down')" class="mtc-tags-icon">
					<Bottom />
				</el-icon>
			</el-tooltip>

			<el-tooltip effect="dark" content="删除">
				<el-icon size="16" v-auth="'menu:Delete'" @click="handleDeleteMenu()" class="mtc-tags-icon">
					<Delete />
				</el-icon>
			</el-tooltip>
		</div>
	</div>
</template>

<script lang="ts" setup>
import { ref, toRaw, watch, h } from 'vue';
import { ElTree } from 'element-plus';
import { getElementLabelLine } from 'element-tree-line';
import { Search } from '@element-plus/icons-vue';
import SvgIcon from '/@/components/svgIcon/index.vue';
import { lazyLoadMenu, menuMoveUp, menuMoveDown } from '../../api';
import { warningNotification } from '/@/utils/message';
import { TreeTypes, MenuTreeItemType } from '../../types';
import type Node from 'element-plus/es/components/tree/src/model/node';

interface IProps {
	treeData: TreeTypes[];
}

const ElementTreeLine = getElementLabelLine(h);

const defaultTreeProps: any = {
	children: 'children',
	label: 'name',
	icon: 'icon',
	isLeaf: (data: TreeTypes[], node: Node) => {
		if (node.data.is_catalog) {
			return false;
		} else {
			return true;
		}
	},
};

const treeRef = ref<InstanceType<typeof ElTree>>();

withDefaults(defineProps<IProps>(), {
	treeData: () => [],
});
const emit = defineEmits(['treeClick', 'deleteDept', 'updateDept']);

let filterVal = ref('');
let sortDisable = ref(false);
let treeSelectMenu = ref<Partial<MenuTreeItemType>>({});
let treeSelectNode = ref<Node | null>(null);

watch(filterVal, (val) => {
	treeRef.value!.filter(val);
});

/**
 * 树的搜索事件
 */
const filterNode = (value: string, data: any) => {
	if (!value) return true;
	return toRaw(data).name.indexOf(value) !== -1;
};

/**
 * 树的懒加载
 */
const handleTreeLoad = (node: Node, resolve: Function) => {
	if (node.level !== 0) {
		lazyLoadMenu({ parent: node.data.id }).then((res: APIResponseData) => {
			resolve(res.data);
		});
	}
};

/**
 * 树的点击事件
 */
const handleNodeClick = (record: MenuTreeItemType, node: Node) => {
	treeSelectMenu.value = record;
	treeSelectNode.value = node;
	emit('treeClick', record);
};

/**
 * 点击左侧编辑按钮
 */
const handleUpdateMenu = (type: string) => {
	if (type === 'update') {
		if (!treeSelectMenu.value.id) {
			warningNotification('请选择菜单！');
			return;
		}
		emit('updateDept', type, treeSelectMenu.value);
	} else {
		emit('updateDept', type);
	}
};

/**
 * 删除菜单
 */
const handleDeleteMenu = () => {
	if (!treeSelectMenu.value.id) {
		warningNotification('请选择菜单！');
		return;
	}
	emit('deleteDept', treeSelectMenu.value.id, () => {
		treeSelectMenu.value = {};
	});
};

/**
 * 移动操作
 */
const handleSort = async (type: string) => {
	if (!treeSelectMenu.value.id) {
		warningNotification('请选择菜单！');
		return;
	}
	if (sortDisable.value) return;

	const parentList = treeSelectNode.value?.parent.childNodes || [];
	const index = parentList.findIndex((i) => i.data.id === treeSelectMenu.value.id);
	const record = parentList.find((i) => i.data.id === treeSelectMenu.value.id);

	if (type === 'up') {
		if (index === 0) return;
		parentList.splice(index - 1, 0, record as any);
		parentList.splice(index + 1, 1);
		sortDisable.value = true;
		await menuMoveUp({ menu_id: treeSelectMenu.value.id });
		sortDisable.value = false;
	}
	if (type === 'down') {
		parentList.splice(index + 2, 0, record as any);
		parentList.splice(index, 1);
		sortDisable.value = true;
		await menuMoveDown({ menu_id: treeSelectMenu.value.id });
		sortDisable.value = false;
	}
};

defineExpose({
	treeRef,
});
</script>

<style lang="scss" scoped>
.menu-tree-com {
	.mtc-head {
		display: flex;
		align-items: center;
		margin-left: -8px;
		color: #606266;
		font-weight: 600;

		.mtc-head-icon {
			margin-right: 8px;
			position: relative;
			top: -1px;
		}

		.mtc-tooltip {
			margin-left: 5px;
			position: relative;
			top: -1px;
		}
	}

	.mtc-tags {
		height: 40px;
		position: absolute;
		bottom: 0;
		left: 0;
		right: 0;
		padding: 0 20px;
		display: flex;
		align-items: center;
		justify-content: space-around;
		box-sizing: border-box;

		.mtc-tags-icon {
			cursor: pointer;
			color: var(--el-color-primary);
		}
	}
}
</style>

<style lang="scss">
.menu-tree-com {
	height: calc(100% - 60px);
	padding: 20px;
	box-sizing: border-box;
	overflow-y: auto;

	.el-tree-node__content {
		height: 32px !important;
	}

	.el-tree .el-tree-node__expand-icon svg {
		display: none !important;
		height: 0;
		width: 0;
	}

	.el-tree-node__expand-icon {
		font-size: 16px;
	}

	.el-tree-node__content > .el-tree-node__expand-icon {
		padding: 0;
		box-sizing: border-box;
		margin-right: 5px;
		margin-left: 24px;
	}

	.el-tree .el-tree-node__expand-icon.expanded {
		-webkit-transform: rotate(0deg);
		transform: rotate(0deg);
	}

	.el-tree .el-tree-node__expand-icon.is-leaf {
		margin-left: 0;
	}

	.el-tree .el-tree-node__expand-icon:before {
		background: url('../../../../../assets/img/menu-tree-show-icon.png') no-repeat center / 100%;
		content: '';
		display: block;
		width: 24px;
		height: 24px;
	}

	.el-tree .el-tree-node__expand-icon.expanded:before {
		background: url('../../../../../assets/img/menu-tree-hidden-icon.png') no-repeat center / 100%;
		content: '';
		display: block;
		width: 24px;
		height: 24px;
	}

	.el-tree .is-leaf.el-tree-node__expand-icon::before {
		display: block;
		background: none !important;
		content: '';
		width: 18px;
		height: 18px;
		border: none;
	}
}
</style>
