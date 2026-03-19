<template>
	<el-input v-model="filterVal" :prefix-icon="Search" placeholder="请输入部门名称" />
	<div class="dept-tree-com">
		<div class="tc-head">
			<el-icon size="16" color="#606266" class="tc-head-icon">
				<HomeFilled />
			</el-icon>
			<span class="tc-head-txt">部门架构</span>
			<el-icon size="16" color="#606266" @click="() => (showTotalNum = !showTotalNum)" class="tc-head-icon">
				<View v-show="!showTotalNum" />
				<Hide v-show="showTotalNum" />
			</el-icon>
		</div>

		<el-tree
			ref="treeRef"
			:data="treeData"
			:props="defaultTreeProps"
			:filter-node-method="handleFilterTreeNode"
			:load="handleLoadNode"
			lazy
			:indent="38"
			@node-click="handleNodeClick"
			highlight-current
		>
			<template #default="{ node, data }">
				<element-tree-line :node="node" :showLabelLine="false" :indent="32">
					<span v-if="data.status" class="text-center font-black font-normal">
						<SvgIcon name="iconfont icon-shouye" color="var(--el-color-primary)" />&nbsp;{{ node.label }}
						<span v-show="showTotalNum">（{{ data.dept_user_count }}人）</span>
					</span>
					<span v-else color="var(--el-color-primary)"> <SvgIcon name="iconfont icon-shouye" />&nbsp;{{ node.label }} </span>
				</element-tree-line>
			</template>
		</el-tree>

		<div class="tree-tags">
			<el-tooltip effect="dark" content="新增">
				<el-icon size="16" @click="handleUpdateMenu('create')" class="mlt-icon">
					<Plus />
				</el-icon>
			</el-tooltip>

			<el-tooltip effect="dark" content="编辑">
				<el-icon size="16" @click="handleUpdateMenu('update')" class="mlt-icon">
					<Edit />
				</el-icon>
			</el-tooltip>

			<el-tooltip effect="dark" content="上移">
				<el-icon size="16" @click="handleSort('up')" class="mlt-icon">
					<Top />
				</el-icon>
			</el-tooltip>

			<el-tooltip effect="dark" content="下移">
				<el-icon size="16" @click="handleSort('down')" class="mlt-icon">
					<Bottom />
				</el-icon>
			</el-tooltip>

			<el-tooltip effect="dark" content="删除">
				<el-icon size="16" @click="handleDeleteDept" class="mlt-icon">
					<Delete />
				</el-icon>
			</el-tooltip>
		</div>
	</div>
</template>

<script lang="ts" setup>
import { ref, watch, toRaw, h } from 'vue';
import { ElTree } from 'element-plus';
import { getElementLabelLine } from 'element-tree-line';
import { Search } from '@element-plus/icons-vue';
import { lazyLoadDept, deptMoveUp, deptMoveDown } from '../../api';
import { warningNotification } from '/@/utils/message';
import { TreeItemType, APIResponseData } from '../../types';
import type Node from 'element-plus/es/components/tree/src/model/node';

interface IProps {
	treeData: TreeItemType[];
}

const ElementTreeLine = getElementLabelLine(h);

const defaultTreeProps: any = {
	children: 'children',
	label: 'name',
	isLeaf: (data: TreeItemType[], node: Node) => {
		if (node.data.hasChild) {
			return false;
		} else {
			return true;
		}
	},
};

withDefaults(defineProps<IProps>(), {
	treeData: () => [],
});
const emit = defineEmits(['treeClick', 'deleteDept', 'updateDept']);

let filterVal = ref('');
let showTotalNum = ref(false);
let sortDisable = ref(false);
let treeSelectDept = ref<TreeItemType>({});
let treeSelectNode = ref<Node | null>(null);
const treeRef = ref<InstanceType<typeof ElTree>>();

watch(filterVal, (val) => {
	treeRef.value!.filter(val);
});

/**
 * 部门树的搜索事件
 */
const handleFilterTreeNode = (value: string, data: TreeItemType) => {
	if (!value) return true;
	return toRaw(data).name?.indexOf(value) !== -1;
};

/**
 * 部门树的懒加载
 */
const handleLoadNode = (node: Node, resolve: Function) => {
	if (node.level !== 0) {
		lazyLoadDept({ parent: node.data.id }).then((res: APIResponseData) => {
			resolve(res.data);
		});
	}
};

/**
 * 部门的点击事件
 */
const handleNodeClick = (record: TreeItemType, node: Node) => {
	treeSelectDept.value = record;
	treeSelectNode.value = node;
	emit('treeClick', record);
};

/**
 * 新增 or 编辑 操作
 */
const handleUpdateMenu = (type: string) => {
	if (type === 'update') {
		if (!treeSelectDept.value.id) {
			warningNotification('请选择菜单！');
			return;
		}
		emit('updateDept', type, treeSelectDept.value);
	} else {
		emit('updateDept', type);
	}
};

/**
 * 删除部门
 */
const handleDeleteDept = () => {
	if (!treeSelectDept.value.id) {
		warningNotification('请选择菜单！');
		return;
	}
	emit('deleteDept', treeSelectDept.value.id, () => {
		treeSelectDept.value = {};
	});
};

/**
 * 部门上下移动操作
 */
const handleSort = async (type: string) => {
	if (!treeSelectDept.value.id) {
		warningNotification('请选择菜单！');
		return;
	}
	if (sortDisable.value) return;

	const parentList = treeSelectNode.value?.parent.childNodes || [];
	const index = parentList.findIndex((i) => i.data.id === treeSelectDept.value.id);
	const record = parentList.find((i) => i.data.id === treeSelectDept.value.id);

	if (type === 'up') {
		if (index === 0) return;
		parentList.splice(index - 1, 0, record as any);
		parentList.splice(index + 1, 1);
		sortDisable.value = true;
		await deptMoveUp({ dept_id: treeSelectDept.value.id });
		sortDisable.value = false;
	}
	if (type === 'down') {
		parentList.splice(index + 2, 0, record as any);
		parentList.splice(index, 1);
		sortDisable.value = true;
		await deptMoveDown({ dept_id: treeSelectDept.value.id });
		sortDisable.value = false;
	}
};

defineExpose({
	treeRef,
});
</script>

<style lang="scss" scoped>
.tc-head {
	display: flex;
	align-items: center;
	margin-left: -8px;
	color: #606266;
	font-weight: 600;

	.tc-head-txt {
		margin: 0 8px;
	}

	.tc-head-icon {
		position: relative;
		top: -1px;
		cursor: pointer;
	}
}

.tree-tags {
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

	.mlt-icon {
		cursor: pointer;
		color: var(--el-color-primary);
	}
}
</style>

<style lang="scss">
.dept-tree-com {
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
		margin-left: 20px;
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
