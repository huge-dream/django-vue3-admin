<template>
  <div class="dashboard-index">
    <BuyerDashboard v-if="hasBuyerRole && !hasSupplierRole" />
    <SupplierDashboard v-else-if="hasSupplierRole && !hasBuyerRole" />
    <div v-else-if="hasBothRoles" class="role-select">
      <el-radio-group v-model="currentRole">
        <el-radio-button label="buyer">采购方看板</el-radio-button>
        <el-radio-button label="supplier">供应商看板</el-radio-button>
      </el-radio-group>
      <BuyerDashboard v-if="currentRole === 'buyer'" />
      <SupplierDashboard v-else />
    </div>
    <el-empty v-else description="您暂无看板权限" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useDashboardStore } from '/@/stores/modules/dashboard';
import BuyerDashboard from './BuyerDashboard.vue';
import SupplierDashboard from './SupplierDashboard.vue';

const store = useDashboardStore();
const { buyer, supplier } = storeToRefs(store);

const currentRole = ref('buyer');

const hasBuyerRole = computed(() => !!buyer.value);
const hasSupplierRole = computed(() => !!supplier.value);
const hasBothRoles = computed(() => hasBuyerRole.value && hasSupplierRole.value);

store.fetchDashboard();
</script>

<style scoped lang="scss">
.dashboard-index {
  padding: 20px;
  .role-select {
    .el-radio-group {
      margin-bottom: 20px;
    }
  }
}
</style>
