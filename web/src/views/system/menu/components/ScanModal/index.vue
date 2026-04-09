<template>
  <el-dialog
    v-model="visible"
    :title="dialogTitle"
    :width="dialogWidth"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <!-- 第一步：选择 App -->
    <div v-if="step === 1" class="scan-step1">
      <el-form label-width="100px">
        <el-form-item :label="$t('message.pages.menu.scan.targetApp')">
          <el-select
            v-model="selectedApp"
            :placeholder="$t('message.pages.menu.scan.selectAppPlaceholder')"
            filterable
            style="width: 100%"
            @change="handleAppChange"
          >
            <el-option
              v-for="app in appList"
              :key="app"
              :label="app"
              :value="app"
            />
          </el-select>
        </el-form-item>
      </el-form>
    </div>

    <!-- 第二步：扫描结果预览 -->
    <div v-else-if="step === 2" class="scan-step2">
      <div class="step2-header">
        <span>{{ $t('message.pages.menu.scan.targetApp') }}: <strong>{{ selectedApp }}</strong></span>
        <span>{{ $t('message.pages.menu.scan.selectedCount', { count: selectedCount }) }}</span>
      </div>

      <el-table
        :data="tableData"
        border
        style="width: 100%; margin-top: 12px"
        max-height="500"
        size="small"
      >
        <el-table-column type="selection" width="45" fixed />
        <el-table-column prop="viewset" :label="$t('message.pages.menu.scan.viewset')" width="180">
          <template #default="{ row }">
            <el-tag size="small" type="info">{{ row.viewset }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="path" :label="$t('message.pages.menu.scan.path')" min-width="200" />
        <el-table-column prop="method" :label="$t('message.pages.menu.scan.method')" width="80">
          <template #default="{ row }">
            <el-tag
              size="small"
              :type="methodTagType(row.method)"
              effect="plain"
            >{{ row.method }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('message.pages.menu.scan.name')" min-width="140">
          <template #default="{ row }">
            <el-input
              v-if="row._editing"
              v-model="row._editName"
              size="small"
              @blur="row._editName = row._editName; row._editing = false"
              @keyup.enter="row._editName = row._editName; row._editing = false"
            />
            <span v-else class="cell-editable" :class="{ 'is-disabled': row.is_existing }" @click="startEdit(row, 'name')">{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('message.pages.menu.scan.value')" min-width="160">
          <template #default="{ row }">
            <el-input
              v-if="row._editingValue"
              v-model="row._editValue"
              size="small"
              @blur="row._editValue = row._editValue; row._editingValue = false"
              @keyup.enter="row._editValue = row._editValue; row._editingValue = false"
            />
            <span v-else class="cell-editable" :class="{ 'is-disabled': row.is_existing }" @click="startEdit(row, 'value')">{{ row.value }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="$t('message.pages.menu.scan.status')" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.is_existing" type="info" size="small">{{ $t('message.pages.menu.scan.existing') }}</el-tag>
            <el-tag v-else type="success" size="small">{{ $t('message.pages.menu.scan.new') }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">{{ $t('message.pages.menu.buttons.cancel') }}</el-button>
        <el-button v-if="step === 2" @click="step = 1">{{ $t('message.pages.menu.scan.back') }}</el-button>
        <el-button
          v-if="step === 1"
          type="primary"
          :loading="scanning"
          :disabled="!selectedApp"
          @click="handleScan"
        >
          {{ $t('message.pages.menu.scan.startScan') }}
        </el-button>
        <el-button
          v-else
          type="primary"
          :loading="submitting"
          :disabled="selectedCount === 0"
          @click="handleSubmit"
        >
          {{ $t('message.pages.menu.scan.confirmGenerate') }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { ElMessage } from 'element-plus';
import { scanGetApps, scanViewSet, scanBatchCreate } from '../../api';

const props = defineProps<{
  modelValue: boolean;
  menuId: number | null;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', val: boolean): void;
  (e: 'success'): void;
}>();

// --- 状态 ---
const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
});

const step = ref(1);
const dialogTitle = computed(() => step.value === 1
  ? '自动扫描接口权限'
  : '扫描结果预览'
);
const dialogWidth = computed(() => step.value === 1 ? '500px' : '90%');

const appList = ref<string[]>([]);
const selectedApp = ref('');
const scanning = ref(false);
const submitting = ref(false);
const tableData = ref<any[]>([]);

// --- 计算属性 ---
const selectedCount = computed(() => {
  return tableData.value.filter(row => !row.is_existing).length;
});

// --- 方法 ---
const methodTagType = (method: string) => {
  const map: Record<string, string> = {
    GET: 'success', POST: 'primary', PUT: 'warning', PATCH: 'warning', DELETE: 'danger',
  };
  return map[method] || 'info';
};

const startEdit = (row: any, field: 'name' | 'value') => {
  if (row.is_existing) return;
  if (field === 'name') {
    row._editName = row.name;
    row._editing = true;
  } else {
    row._editValue = row.value;
    row._editingValue = true;
  }
};

const loadApps = async () => {
  try {
    const res: any = await scanGetApps();
    appList.value = res.data || [];
  } catch {
    appList.value = [];
  }
};

const handleAppChange = () => {
  step.value = 1;
  tableData.value = [];
};

const handleScan = async () => {
  if (!selectedApp.value) return;
  scanning.value = true;
  try {
    const res: any = await scanViewSet(selectedApp.value);
    const flatData: any[] = [];
    for (const group of (res.data || [])) {
      for (const btn of group.buttons) {
        flatData.push({
          ...btn,
          _editing: false,
          _editName: btn.name,
          _editingValue: false,
          _editValue: btn.value,
        });
      }
    }
    tableData.value = flatData;
    if (flatData.length === 0) {
      ElMessage.warning('该 App 下未检测到 ViewSet 接口');
    } else {
      step.value = 2;
    }
  } catch (err: any) {
    ElMessage.error(err?.message || '扫描失败');
  } finally {
    scanning.value = false;
  }
};

const handleSubmit = async () => {
  if (!props.menuId) {
    ElMessage.warning('未选中菜单');
    return;
  }
  const selected = tableData.value
    .filter(row => !row.is_existing)
    .map(row => ({
      path: row.path,
      method: row.method,
      action: row.action,
      name: row._editName || row.name,
      value: row._editValue || row.value,
      method_int: row.method_int,
    }));

  if (selected.length === 0) {
    ElMessage.warning('请至少选择一项');
    return;
  }

  submitting.value = true;
  try {
    const res: any = await scanBatchCreate(props.menuId, selected);
    ElMessage.success(res?.msg || `已创建 ${selected.length} 项`);
    emit('success');
    handleClose();
  } catch (err: any) {
    ElMessage.error(err?.message || '创建失败');
  } finally {
    submitting.value = false;
  }
};

const handleClose = () => {
  visible.value = false;
  step.value = 1;
  selectedApp.value = '';
  tableData.value = [];
};

const handleOpen = async () => {
  await loadApps();
};

defineExpose({ handleOpen });
</script>

<style scoped lang="scss">
.scan-step1 {
  padding: 20px 0;
}

.scan-step2 {
  .step2-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 14px;
    color: #606266;
  }
}

.cell-editable {
  cursor: pointer;
  &:hover:not(.is-disabled) {
    color: var(--el-color-primary);
    text-decoration: underline;
  }
  &.is-disabled {
    cursor: not-allowed;
    color: #999;
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
