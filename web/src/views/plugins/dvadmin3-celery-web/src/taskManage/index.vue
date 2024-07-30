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
                            <p>{{ item.interval || item.crontab || '--' }}</p>
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
                                               cancel-button-text="取消"
                                               :title="item.enabled ? '确认停用该任务？' : '确认启用该任务？'">
                                    <template #reference>
                                        <el-tag v-if="item.enabled == true" type="success" effect="dark">已启用</el-tag>
                                        <el-tag v-else type="danger" effect="dark">已停用</el-tag>
                                    </template>
                                </el-popconfirm>
                            </div>
                            <!--                            <div class="ml-2">-->
                            <!--                                <el-popconfirm width="180" confirm-button-text="确定" @confirm="runTask(item)"-->
                            <!--                                               cancel-button-text="取消" title="立即运行该任务？">-->
                            <!--                                    <template #reference>-->
                            <!--                                        <el-button size="small" circle>-->
                            <!--                                            <el-icon>-->
                            <!--                                                <CaretRight/>-->
                            <!--                                            </el-icon>-->
                            <!--                                        </el-button>-->
                            <!--                                    </template>-->
                            <!--                                </el-popconfirm>-->
                            <!--                            </div>-->
                        </div>
                        <div class="taskName">
                            <el-dropdown trigger="hover" class="ml-2">
                                <el-button type="primary" size="small" circle effect>
                                    <el-icon>
                                        <Edit/>
                                    </el-icon>
                                </el-button>
                                <template #dropdown>
                                    <el-dropdown-menu>
                                        <el-dropdown-item :icon="Cpu" @click="runTask(item)">运行</el-dropdown-item>
                                        <el-dropdown-item :icon="Edit" @click="editTask(item)">编辑</el-dropdown-item>
                                        <el-dropdown-item :icon="Delete" @click="del(item)" divided>删除
                                        </el-dropdown-item>
                                    </el-dropdown-menu>
                                </template>
                            </el-dropdown>

                            <el-button type="primary" size="small" circle plain @click="taskLogs(item)" class="ml-2">
                                <el-icon>
                                    <Monitor/>
                                </el-icon>
                            </el-button>
                        </div>
                    </div>
                </el-card>
            </el-col>
            <el-col :xl="4" :lg="6" :md="8" :sm="12" :xs="24">
                <el-card class="task task-add" shadow="never" @click="addTaskShow">
                    <el-icon>
                        <Plus/>
                    </el-icon>
                    <p>添加计划任务</p>
                </el-card>
                <el-dialog v-model="addTaskDialogVisible" title="添加任务" width="24%" class="el-dialog">
                    <el-form ref="addTaskFormRef" :rules="rules" :model="addTaskForm" label-width="120px"
                             label-position="left">
                        <el-row>
                            <el-col>
                                <el-form-item label="任务名称" required prop="name">
                                    <el-input v-model="addTaskForm.name"/>
                                </el-form-item>
                            </el-col>
                            <el-col>
                                <el-form-item label="任务" required prop="task">
                                    <el-select v-model="addTaskForm.task" @focus="loadTaskList" class="w-full">
                                        <el-option v-for="item in selectedTaskList" :key="item.value"
                                                   :label="item.label"
                                                   :value="item.value"/>
                                    </el-select>
                                </el-form-item>
                            </el-col>
                            <el-col>
                                <el-form-item label="使用调度模型" required prop="schedule">
                                    <el-switch active-text="CrontabSchedule" inactive-text="IntervalSchedule"
                                               :active-value="1"
                                               :inactive-value="0"
                                               v-model="addTaskForm.scheduleType"/>
                                </el-form-item>
                                <div v-show="addTaskForm.scheduleType==0">
                                    <el-form-item label="调度模型" required>
                                        <el-select v-model="addTaskForm.schedule" @focus="loadIntervalScheduleList"
                                                   class="w-full" clearable>
                                            <el-option v-for="item in intervalScheduleList" :key="item.value"
                                                       :value="item.id"
                                                       :label="`every: ${item.every}; period: ${item.period}`"
                                            >
                                                <template #default>
                                                    <div class="flex justify-between">
                                                        <span>every: {{ item.every }}</span>
                                                        <span>period: {{ item.period }}</span>
                                                    </div>
                                                </template>
                                            </el-option>
                                        </el-select>
                                    </el-form-item>
                                </div>
                                <div v-show="addTaskForm.scheduleType==1">
                                    <el-form-item label="调度模型" required>
                                        <el-select v-model="addTaskForm.schedule" @focus="loadCrontabScheduleList"
                                                   class="w-full" clearable>
                                            <el-option v-for="item in crontabScheduleList" :key="item.value"
                                                       :value="item.id"
                                                       :label="`minute: ${item.minute}; hour: ${item.hour}; day_of_week: ${item.day_of_week}; day_of_month: ${item.day_of_month}; month_of_year: ${item.month_of_year}`"
                                            >
                                                <template #default>
                                                    <div class="flex justify-between">
                                                        <span>minute: {{ item.minute }};</span>
                                                        <span>hour: {{ item.hour }};</span>
                                                        <span>day_of_week: {{ item.day_of_week }};</span>
                                                        <span>day_of_month: {{ item.day_of_month }};</span>
                                                        <span>month_of_year: {{ item.month_of_year }};</span>
                                                    </div>
                                                </template>
                                            </el-option>
                                        </el-select>
                                    </el-form-item>
                                </div>
                            </el-col>
                            <el-col>
                                <el-form-item label="是否启用" required prop="enabled">
                                    <el-switch v-model="addTaskForm.enabled"/>
                                </el-form-item>
                            </el-col>
                        </el-row>
                    </el-form>
                    <template #footer>
                      <span class="dialog-footer">
                        <el-button @click="addTaskDialogVisible = false">取消</el-button>
                        <el-button type="primary" @click="addTask(addTaskFormRef)">
                          确定
                        </el-button>
                      </span>
                    </template>

                </el-dialog>
                <el-dialog v-model="editTaskDialogVisible" title="编辑任务" width="24%" class="el-dialog">
                    <el-form ref="editTaskFormRef" :rules="rules" :model="editTaskForm" label-width="120px"
                             label-position="left">
                        <el-row>
                            <el-col>
                                <el-form-item label="任务名称" required prop="name">
                                    <el-input v-model="editTaskForm.name"/>
                                </el-form-item>
                            </el-col>
                            <el-col>
                                <el-form-item label="任务" required prop="task">
                                    <el-select v-model="editTaskForm.task" @focus="loadTaskList" class="w-full">
                                        <el-option v-for="item in selectedTaskList" :key="item.value"
                                                   :label="item.label"
                                                   :value="item.value"/>
                                    </el-select>
                                </el-form-item>
                            </el-col>
                            <el-col>
                                <el-form-item label="使用调度模型" required prop="schedule">
                                    <el-switch active-text="CrontabSchedule" inactive-text="IntervalSchedule"
                                               :active-value="1"
                                               :inactive-value="0"
                                               v-model="editTaskForm.scheduleType"/>
                                </el-form-item>
                                <div v-show="editTaskForm.scheduleType==0">
                                    <el-form-item label="调度模型" required>
                                        <el-select v-model="editTaskForm.schedule" @focus="loadIntervalScheduleList"
                                                   class="w-full" clearable>
                                            <el-option v-for="item in intervalScheduleList" :key="item.value"
                                                       :value="item.id"
                                                       :label="`every: ${item.every}; period: ${item.period}`"
                                            >
                                                <template #default>
                                                    <div class="flex justify-between">
                                                        <span>every: {{ item.every }}</span>
                                                        <span>period: {{ item.period }}</span>
                                                    </div>
                                                </template>
                                            </el-option>
                                        </el-select>
                                    </el-form-item>
                                </div>
                                <div v-show="editTaskForm.scheduleType==1">
                                    <el-form-item label="调度模型" required>
                                        <el-select v-model="editTaskForm.schedule" @focus="loadCrontabScheduleList"
                                                   class="w-full" clearable>
                                            <el-option v-for="item in crontabScheduleList" :key="item.value"
                                                       :value="item.id"
                                                       :label="`minute: ${item.minute}; hour: ${item.hour}; day_of_week: ${item.day_of_week}; day_of_month: ${item.day_of_month}; month_of_year: ${item.month_of_year}`"
                                            >
                                                <template #default>
                                                    <div class="flex justify-between">
                                                        <span>minute: {{ item.minute }};</span>
                                                        <span>hour: {{ item.hour }};</span>
                                                        <span>day_of_week: {{ item.day_of_week }};</span>
                                                        <span>day_of_month: {{ item.day_of_month }};</span>
                                                        <span>month_of_year: {{ item.month_of_year }};</span>
                                                    </div>
                                                </template>
                                            </el-option>
                                        </el-select>
                                    </el-form-item>
                                </div>
                            </el-col>
                            <el-col>
                                <el-form-item label="是否启用" required prop="enabled">
                                    <el-switch v-model="editTaskForm.enabled"/>
                                </el-form-item>
                            </el-col>
                        </el-row>
                    </el-form>
                    <template #footer>
                      <span class="dialog-footer">
                        <el-button @click="editTaskDialogVisible = false">取消</el-button>
                        <el-button type="primary" @click="submitEditTask(editTaskFormRef)">
                          确定
                        </el-button>
                      </span>
                    </template>

                </el-dialog>
                <el-dialog v-model="showTaskDialogVisible" title="任务运行日志" width="50%" class="rounded-lg"
                           destroy-on-close>
                    <div style="height: 800px;  position: relative">
                        <taskLog :taskItem="selectedTask"></taskLog>
                    </div>
                </el-dialog>
            </el-col>
        </el-row>
    </el-main>
</template>

<script setup lang="ts" name="taskManage">
import {Edit, Delete, ArrowDown, Cpu} from '@element-plus/icons-vue';
import * as api from './api'
import {ref, onMounted, reactive, defineAsyncComponent, toRaw, watch} from 'vue';
import {errorMessage, successMessage} from '/@/utils/message';
import {FormInstance, FormRules} from "element-plus";

const taskLog = defineAsyncComponent(() => import('./component/taskLog/index.vue'));

const addTaskDialogVisible = ref(false);

const editTaskDialogVisible = ref(false);

const showTaskDialogVisible = ref(false);

const showCron = ref(false);

const addTaskForm = reactive({
    name: '',
    task: '',
    scheduleType: 0,//0 IntervalSchedule 1 CrontabSchedule
    schedule: '',
    enabled: true,
})

let editTaskForm = reactive({
    id: '',
    name: '',
    task: '',
    scheduleType: null,//0 IntervalSchedule 1 CrontabSchedule
    schedule: '',
    enabled: true,
})

const addTaskFormRef = ref<FormInstance>()

const editTaskFormRef = ref<FormInstance>()

interface addTaskFormRules {
    name: string,
    task: string,
    schedule: string,
    enabled: string,
}

const rules = reactive<FormRules<addTaskFormRules>>({
    name: [
        {required: true, message: '请输入任务名称', trigger: 'blur'},
    ], task: [
        {required: true, message: '请选择一个任务', trigger: 'blur'},
    ], schedule: [
        {required: true, message: '请选择schedule', trigger: 'blur'},
    ], enabled: [
        {required: true, message: '请选择状态', trigger: 'blur'},
    ],
})

const taskList = ref([]) as any;

const selectedTaskList = ref({}) as any;

const intervalScheduleList = ref({}) as any;

const crontabScheduleList = ref({}) as any;

let selectedTask = ref({})

/*
* 加载任务列表
* */
const loadTaskList = () => {
    api.getBackendTaskList({}).then((res: APIResponseData) => {
        if (res.code === 2000) {
            selectedTaskList.value = res.data
        }
    })
}

const loadIntervalScheduleList = () => {
    api.getIntervalScheduleList({}).then((res: APIResponseData) => {
        if (res.code === 2000) {
            intervalScheduleList.value = res.data
        }
    })
}

const loadCrontabScheduleList = () => {
    api.getCrontabScheduleList({}).then((res: APIResponseData) => {
        if (res.code === 2000) {
            crontabScheduleList.value = res.data
        }
    })
}

/**
 * 运行任务
 * @param item 任务
 */

const runTask = (item: any) => {
    api.RunTask(item).then((res: APIResponseData) => {
        if (res.code === 2000) {
            return successMessage(res.msg as string)
        }
    })
};

const editTask = (item: any) => {
    for (const key in item) {
        editTaskForm[key] = item[key]
    }
    editTaskDialogVisible.value = true
};

watch(() => editTaskDialogVisible.value, (val) => {
    if (!val) {
        showCron.value = false
        editTaskFormRef.value.resetFields()
    }
})

const submitEditTask = async (formEl: FormInstance | undefined) => {
    if (!formEl) return
    await formEl.validate((valid, fields) => {
        if (valid) {
            api.EditTask(editTaskForm).then((res: APIResponseData) => {
                if (res.code === 2000) {
                    editTaskDialogVisible.value = false;
                    formEl.resetFields()
                    getOrUpdateTaskList()
                    return successMessage(res.msg as string)
                }
            })
        } else {
            errorMessage('请检查表单')
        }
    })
}

/**
 * 任务日志
 * @param item 任务
 */
const taskLogs = (item: any) => {
    selectedTask.value = toRaw(item)
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

const addTaskShow = () => {
    addTaskDialogVisible.value = true;
    selectedTask.value = {}
};

const addTask = async (formEl: FormInstance | undefined) => {
    if (!formEl) return
    await formEl.validate((valid, fields) => {
        if (valid) {
            api.AddTask(addTaskForm).then((res: APIResponseData) => {
                if (res.code === 2000) {
                    addTaskDialogVisible.value = false;
                    formEl.resetFields()
                    getOrUpdateTaskList()
                    return successMessage(res.msg as string)
                }
            })
        } else {
            errorMessage('请检查表单')
        }
    })
}


/**
 * 设置任务状态
 * @param item 任务
 */

const setTaskStatus = (item: any) => {
    item.enabled = !item.enabled;
    api.UpdateTask({enabled: item.enabled, id: item.id}).then((res: APIResponseData) => {
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
