<template>
  <div class="dashboard-index">
    <!-- 切换角色时显示 -->
    <div v-if="showRoleSwitch" class="role-select">
      <el-radio-group v-model="currentRole">
        <el-radio-button label="buyer">采购方仪表盘</el-radio-button>
        <el-radio-button label="supplier">供应商仪表盘</el-radio-button>
      </el-radio-group>
    </div>
    <BuyerDashboard v-if="currentRole === 'buyer'" />
    <SupplierDashboard v-else-if="isSupplierDashboardRole(currentRole)" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { storeToRefs } from 'pinia';
import { useDashboardStore } from '/@/stores/modules/dashboard';
import mittBus from '/@/utils/mitt';
import BuyerDashboard from './BuyerDashboard.vue';
import SupplierDashboard from './SupplierDashboard.vue';

const route = useRoute();
const store = useDashboardStore();
const { buyer, supplier } = storeToRefs(store);

const currentRole = ref('buyer');

/** 供应商侧仪表盘：角色标识为 supplier_*（如 supplier_quote），兼容历史值 supplier */
const isSupplierDashboardRole = (role: string) =>
  role === 'supplier' || /^supplier_/.test(role);

const hasBuyerRole = computed(() => !!buyer.value);
const hasSupplierRole = computed(() => !!supplier.value);
const hasBothRoles = computed(() => hasBuyerRole.value && hasSupplierRole.value);

// 超级管理员默认显示采购方，有双方角色时显示切换器
const showRoleSwitch = computed(() => hasBothRoles.value);

// 更新 tagsView 标题
const updateTagsViewTitle = (role: string) => {
  const title = role === 'buyer' ? '采购方仪表盘' : '供应商仪表盘';
  mittBus.emit('onUpdateTagsViewName', { path: route.path, title });
};

// 初始化标题
onMounted(() => {
  updateTagsViewTitle(currentRole.value);
});

// 如果只有采购方权限，默认 buyer
// 如果只有供应商权限，默认 supplier_*（当前为 supplier_quote）
// 初始化时确保 currentRole 与可用角色匹配
if (!hasBuyerRole.value && hasSupplierRole.value) {
  currentRole.value = 'supplier_quote';
}

// 如果后端返回了数据但 currentRole 不匹配角色，则默认 buyer
if (hasBuyerRole.value && !hasBothRoles.value) {
  currentRole.value = 'buyer';
}

// 数据加载后同步 currentRole
watch([hasBuyerRole, hasSupplierRole], () => {
  if (hasBothRoles.value) {
    // 双方角色，默认 buyer
    if (currentRole.value !== 'buyer' && !isSupplierDashboardRole(currentRole.value)) {
      currentRole.value = 'buyer';
    }
  } else if (hasBuyerRole.value) {
    currentRole.value = 'buyer';
  } else if (hasSupplierRole.value) {
    currentRole.value = 'supplier_quote';
  }
});

// currentRole 变化时更新 tagsView 标题
watch(currentRole, (newRole) => {
  updateTagsViewTitle(newRole);
});

store.fetchDashboard();
</script>

<style scoped lang="scss">
.dashboard-index {
  padding: 20px;
  .role-select {
    margin-bottom: 20px;
    .el-radio-group {
      margin-bottom: 0;
    }
  }
}
</style>
