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

    <!-- 第二步：扫描结果预览（分组折叠表格） -->
    <div v-else-if="step === 2" class="scan-step2">
      <div class="step2-header">
        <span>{{ $t('message.pages.menu.scan.targetApp') }}: <strong>{{ selectedApp }}</strong></span>
        <span>{{ $t('message.pages.menu.scan.selectedCount', { count: selectedCount }) }}</span>
      </div>

      <!-- 工具栏：全选/取消全选 -->
      <div class="step2-toolbar">
        <el-button size="small" @click="toggleAll(true)">全选全部</el-button>
        <el-button size="small" @click="toggleAll(false)">取消全选</el-button>
      </div>

      <!-- 分组折叠面板 -->
      <el-collapse v-model="expandedGroups" class="scan-collapse">
        <el-collapse-item
          v-for="group in tableData"
          :key="group.viewset"
          :name="group.viewset"
        >
          <template #title>
            <div class="collapse-header">
              <el-checkbox
                :model-value="isGroupAllSelected(group)"
                :indeterminate="isGroupIndeterminate(group)"
                @change="(val: boolean) => toggleGroup(group, val)"
                @click.stop
              />
              <el-tag size="small" type="info" style="margin-left: 8px">{{ group.viewset }}</el-tag>
              <span class="group-count">{{ group.buttons.length }} {{ $t('message.pages.menu.scan.actions') }}</span>
            </div>
          </template>

          <el-table
            :data="group.buttons"
            border
            size="small"
            style="width: 100%"
            @selection-change="(rows: Button[]) => onSelectionChange(group, rows)"
          >
            <el-table-column type="selection" width="45" :selectable="(row: Button) => !row.is_existing" />
            <el-table-column prop="path" :label="$t('message.pages.menu.scan.path')" min-width="220" />
            <el-table-column prop="method" :label="$t('message.pages.menu.scan.method')" width="80">
              <template #default="{ row }">
                <el-tag size="small" :type="methodTagType(row.method)" effect="plain">{{ row.method }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column :label="$t('message.pages.menu.scan.name')" min-width="150">
              <template #default="{ row }">
                <el-input
                  v-if="row._editing"
                  v-model="row._editName"
                  size="small"
                  @blur="row._editing = false"
                  @keyup.enter="row._editing = false"
                />
                <span
                  v-else
                  class="cell-editable"
                  :class="{ 'is-disabled': row.is_existing }"
                  @click="startEdit(row, 'name')"
                >{{ row.name }}</span>
              </template>
            </el-table-column>
            <el-table-column :label="$t('message.pages.menu.scan.value')" min-width="160">
              <template #default="{ row }">
                <el-input
                  v-if="row._editingValue"
                  v-model="row._editValue"
                  size="small"
                  @blur="row._editingValue = false"
                  @keyup.enter="row._editingValue = false"
                />
                <span
                  v-else
                  class="cell-editable"
                  :class="{ 'is-disabled': row.is_existing }"
                  @click="startEdit(row, 'value')"
                >{{ row.value }}</span>
              </template>
            </el-table-column>
            <el-table-column :label="$t('message.pages.menu.scan.status')" width="90">
              <template #default="{ row }">
                <el-tag v-if="row.is_existing" type="info" size="small">{{ $t('message.pages.menu.scan.existing') }}</el-tag>
                <el-tag v-else type="success" size="small">{{ $t('message.pages.menu.scan.new') }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-collapse-item>
      </el-collapse>
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

interface Button {
  path: string;
  method: string;
  action: string;
  name: string;
  value: string;
  is_existing: boolean;
  method_int: number;
  _editing?: boolean;
  _editName?: string;
  _editingValue?: boolean;
  _editValue?: string;
}

interface ViewSetGroup {
  viewset: string;
  viewset_verbose_name?: string;
  buttons: Button[];
  _selectedSet?: Set<string>; // 追踪该 group 内选中的 row key
}

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
const tableData = ref<ViewSetGroup[]>([]);
const expandedGroups = ref<string[]>([]);

const rowKey = (btn: Button) => `${btn.path}::${btn.method}::${btn.action}`;

// --- 计算属性 ---
const selectedCount = computed(() => {
  return tableData.value.reduce((total, group) => {
    return total + (group._selectedSet?.size || 0);
  }, 0);
});

// --- 方法 ---
const methodTagType = (method: string) => {
  const map: Record<string, string> = {
    GET: 'success', POST: 'primary', PUT: 'warning', PATCH: 'warning', DELETE: 'danger',
  };
  return map[method] || 'info';
};

const isGroupAllSelected = (group: ViewSetGroup) => {
  const selectable = group.buttons.filter(btn => !btn.is_existing);
  return selectable.length > 0 && selectable.every(btn => group._selectedSet?.has(rowKey(btn)));
};

const isGroupIndeterminate = (group: ViewSetGroup) => {
  const selectable = group.buttons.filter(btn => !btn.is_existing);
  const selectedCount = selectable.filter(btn => group._selectedSet?.has(rowKey(btn))).length;
  return selectedCount > 0 && selectedCount < selectable.length;
};

const toggleGroup = (group: ViewSetGroup, checked: boolean) => {
  for (const btn of group.buttons) {
    if (!btn.is_existing) {
      if (checked) {
        group._selectedSet!.add(rowKey(btn));
      } else {
        group._selectedSet!.delete(rowKey(btn));
      }
    }
  }
  // 触发 el-table 的选中状态更新（通过重新设置 data 触发）
  triggerTableRefresh(group);
};

const toggleAll = (checked: boolean) => {
  for (const group of tableData.value) {
    toggleGroup(group, checked);
  }
};

// 触发 el-table 刷新选中状态
const triggerTableRefresh = (group: ViewSetGroup) => {
  const data = [...group.buttons];
  group.buttons = data;
};

const onSelectionChange = (group: ViewSetGroup, selectedRows: Button[]) => {
  const selectedKeys = new Set(selectedRows.map(rowKey));
  // 更新 _selectedSet
  for (const btn of group.buttons) {
    const key = rowKey(btn);
    if (btn.is_existing) {
      group._selectedSet!.delete(key);
    } else if (selectedKeys.has(key)) {
      group._selectedSet!.add(key);
    } else {
      group._selectedSet!.delete(key);
    }
  }
};

const startEdit = (row: Button, field: 'name' | 'value') => {
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
    const groups: ViewSetGroup[] = [];
    for (const group of (res.data || [])) {
      const buttons: Button[] = group.buttons.map((btn: any) => ({
        ...btn,
        _editing: false,
        _editName: btn.name,
        _editingValue: false,
        _editValue: btn.value,
      }));
      const g: ViewSetGroup = {
        viewset: group.viewset,
        viewset_verbose_name: group.viewset_verbose_name,
        buttons,
        _selectedSet: new Set(
          buttons
            .filter(btn => !btn.is_existing)
            .map(rowKey)
        ),
      };
      groups.push(g);
    }
    tableData.value = groups;
    expandedGroups.value = groups.map(g => g.viewset);
    if (groups.length === 0) {
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
  const selected: any[] = [];
  for (const group of tableData.value) {
    for (const btn of group.buttons) {
      if (btn.is_existing) continue;
      if (!group._selectedSet?.has(rowKey(btn))) continue;
      selected.push({
        path: btn.path,
        method: btn.method,
        action: btn.action,
        name: btn._editName || btn.name,
        value: btn._editValue || btn.value,
        method_int: btn.method_int,
      });
    }
  }

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
  expandedGroups.value = [];
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

  .step2-toolbar {
    margin-top: 12px;
    margin-bottom: 8px;
  }
}

.scan-collapse {
  border: 1px solid #ebeef5;
  border-radius: 4px;

  .collapse-header {
    display: flex;
    align-items: center;
    font-size: 14px;
    font-weight: 500;

    .group-count {
      margin-left: auto;
      font-size: 12px;
      color: #909399;
    }
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
