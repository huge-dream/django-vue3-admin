<template>
	<el-main class="bg-gray-100">
		<el-row :gutter="15">
			<el-col :xl="4" :lg="6" :md="8" :sm="12" :xs="24" v-for="item in taskList" :key="item.id">
				<el-card class="task task-item" shadow="hover">
					<h2>{{ item.name }}</h2>
					<ul>
						<li>
							<h4>执行任务</h4>
							<p>{{ item.task }}</p>
						</li>
						<li>
							<h4>定时规则</h4>
							<p>{{ item.interval || item.cron }}</p>
						</li>
						<li>
							<h4>最后运行时间</h4>
							<p>{{ item.last_run_at || '--' }}</p>
						</li>
					</ul>
					<div class="bottom w-full">
						<div class="state flex flex-wrap items-center">
							<div>
								<el-popconfirm width="180" confirm-button-text="确定" @confirm="setTaskStatus(item)"
									cancel-button-text="取消" :title="item.enabled ? '确认停用该任务？' : '确认启用该任务？'">
									<template #reference>
										<el-tag v-if="item.enabled == true" type="success" effect="dark">已启用</el-tag>
										<el-tag v-else type="danger" effect="dark">已停用</el-tag>
									</template>
								</el-popconfirm>
							</div>
							<!-- <div class="ml-2">
								<el-popconfirm width="180" confirm-button-text="确定" @confirm="runTask(item)"
									cancel-button-text="取消" title="立即运行该任务？">
									<template #reference>
										<el-button size="small" circle>
											<el-icon>
												<CaretRight />
											</el-icon>
										</el-button>
									</template>
								</el-popconfirm>
							</div> -->
						</div>
						<div class="taskName">
							<el-dropdown trigger="hover" class="ml-2">
								<el-button type="primary" size="small" circle effect>
									<el-icon>
										<Edit />
									</el-icon>
								</el-button>
								<template #dropdown>
									<el-dropdown-menu>
										<el-dropdown-item :icon="Edit" @click="editTask(item)">编辑</el-dropdown-item>
										<el-dropdown-item :icon="Delete" @click="del(item)" divided>删除</el-dropdown-item>
									</el-dropdown-menu>
								</template>
							</el-dropdown>

							<el-button type="primary" size="small" circle plain @click="taskLogs(item)" class="ml-2">
								<el-icon>
									<Monitor />
								</el-icon>
							</el-button>
						</div>
					</div>
				</el-card>
			</el-col>
			<el-col :xl="4" :lg="6" :md="8" :sm="12" :xs="24">
				<el-card class="task task-add" shadow="never" @click="addTask">
					<el-icon>
						<Plus />
					</el-icon>
					<p>添加计划任务</p>
				</el-card>
				<el-dialog v-model="addTaskDialogVisible" title="添加任务" width="20%" class="el-dialog">
					<el-form :model="addTaskform" label-width="120px" label-position="left">
						<el-row>
							<el-col>
								<el-form-item label="任务名称" required>
									<el-input v-model="addTaskform.name" />
								</el-form-item>
							</el-col>
							<el-col>
								<el-form-item label="任务" required>
									<el-select v-model="addTaskform.task" placeholder="Select">
										<el-option v-for="item in taskList" :key="item.value" :label="item.label"
											:value="item.value" />
									</el-select>
								</el-form-item>
							</el-col>
							<el-col>
								<el-form-item label="corn表达式" required>
									<el-input v-model="addTaskform.corn" placeholder="* * * * * *" />
								</el-form-item>
							</el-col>
							<el-col>
								<el-form-item label="是否启用" required>
									<el-switch v-model="addTaskform.status" />
								</el-form-item>
							</el-col>
						</el-row>
					</el-form>

				</el-dialog>
				<el-dialog v-model="showTaskDialogVisible" title="任务运行日志" width="50%" class="rounded-lg">
					<div style="height: 800px;  position: relative">
						<taskLog :taskItem="selectedTask"></taskLog>
					</div>
				</el-dialog>
			</el-col>
		</el-row>
	</el-main>
</template>

<script setup lang="ts">
import { Edit, Delete } from '@element-plus/icons-vue';
import * as api from './api'
import { ref, onMounted, reactive, defineAsyncComponent, toRaw } from 'vue';
import { successMessage } from '/@/utils/message';
const taskLog = defineAsyncComponent(() => import('./component/taskLog/index.vue'));

const addTaskDialogVisible = ref(false);

const showTaskDialogVisible = ref(false);

const addTaskform = reactive({
	id: '',
	name: '',
	task: '',
	corn: '* * * * * *',
	status: '',
	last_run_at: ''
})

const taskList = ref([]) as any;

let selectedTask = ref({})

// /**
//  * 运行任务
//  * @param item 任务
//  */

// const runTask = (item: any) => {
// 	api.RunTask(item).then((res: APIResponseData) => {
// 		if (res.code === 2000) {
// 			return successMessage(res.msg as string)
// 		}
// 	})
// };

const editTask = (item: any) => {
	console.log(item);
};

/**
 * 任务日志
 * @param item 任务
 */
const taskLogs = (item: any) => {
	selectedTask = toRaw(item)
	showTaskDialogVisible.value = true
};

/**
 * 删除任务
 * @param item 任务
 */

const del = (item: any) => {
	api.DelTask(item).then((res: APIResponseData) => {
		if (res.code === 2000) {
			getOrUpdateTaskList()
			return successMessage(res.msg as string)
		}
	})
};

/**
 * 添加任务弹窗
 */

const addTask = () => {
	addTaskDialogVisible.value = true;
	selectedTask.value = {}
};

/**
 * 设置任务状态
 * @param item 任务
 */

const setTaskStatus = (item: any) => {
	item.enabled = !item.enabled;
	api.UpdateTask({ enabled: item.enabled, id: item.id }).then((res: APIResponseData) => {
		if (res.code === 2000) {
			return successMessage(res.msg as string)
		}
	});

}

/**
 *  加载或更新任务列表
 */

const getOrUpdateTaskList = () => {
	api.getTaskList({}).then((res: APIResponseData) => {
		taskList.value = res.data;
	});
}



onMounted(() => {
	getOrUpdateTaskList()
});


</script>

<style lang="scss" scoped>
.task {
	height: 260px;
}

.task-item h2 {
	font-size: 15px;
	color: #3c4a54;
	padding-bottom: 10px;
}

.task-item li {
	list-style-type: none;
	margin-bottom: 10px;
}

.task-item li h4 {
	font-size: 12px;
	font-weight: normal;
	color: #999;
}

.task-item li p {
	margin-top: 5px;
}

.task-item .bottom {
	border-top: 1px solid #ebeef5;
	text-align: right;
	padding-top: 10px;
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.task-add {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	text-align: center;
	cursor: pointer;
	color: #999;
}

.task-add:hover {
	color: #409eff;
}

.task-add i {
	font-size: 30px;
}

.task-add p {
	font-size: 12px;
	margin-top: 20px;
}

.dark .task-item .bottom {
	border-color: var(--el-border-color-light);
}

.el-card {
	border-radius: 3%;
	overflow: hidden;
}

.el-dialog {
	border-radius: 3%;
	overflow: hidden;
}
</style>
