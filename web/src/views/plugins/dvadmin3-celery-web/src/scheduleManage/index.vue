<template>
    <el-main class="bg-gray-100 h-full">
        <el-card :body-style="{ height: '100%' }">
            <el-tabs v-model="activeTab" class="h-full" @tab-click="handleClick">
                <el-tab-pane label="crontabManage" name="crontabManage" class="h-full">
                    <crontabManage class="h-full"></crontabManage>
                </el-tab-pane>
                <el-tab-pane label="intervalManage" name="intervalManage">
                    <intervalManage></intervalManage>
                </el-tab-pane>
            </el-tabs>
        </el-card>
    </el-main>
</template>
<script lang="ts" setup>
import { defineAsyncComponent, ref } from 'vue'
const crontabManage = defineAsyncComponent(() => import('./component/crontabManage/index.vue'));
const intervalManage = defineAsyncComponent(() => import('./component/intervalManage/index.vue'));
const activeTab = ref('crontabManage')

const handleClick = (tab: any, event: Event) => {
    const { paneName } = tab
    activeTab.value = paneName
}
</script>

<style lang="scss" scoped>
.el-tabs--card {
    height: calc(100vh - 300px);
    /* overflow-y: auto; */
}

.el-tab-pane {
    height: calc(100vh - 300px);
    overflow-y: auto;
}
</style>