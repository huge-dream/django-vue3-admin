<template>
  <div class="section-builder">
    <div class="header">
      <div v-if="!hideTitle" class="title">{{ titleText }}</div>
      <div v-else class="title-spacer" />
    </div>

    <el-empty v-if="!localSections.length" description="暂无分段，点击新增" />

    <el-tabs v-else v-model="active" type="card">
      <el-tab-pane v-for="sec in visibleSections" :key="sec.__id" :name="sec.__id">
        <template #label>
          <span :class="['tab-label', sec.enabled && 'tab-label--on']">{{ sec.title || '未命名' }}</span>
        </template>

        <div class="pane-header">
          <el-input v-if="showTitleInput" v-model="sec.title" placeholder="分段名称" size="small" class="w-220" :disabled="isReadonly" />
          <el-switch
            v-if="canToggleSupplierAdd(sec)"
            v-model="sec.supplierCanAddRow"
            active-text="供应商可增行"
            :disabled="isReadonly"
          />
          <div class="flex-spacer" />
          <el-button v-if="sec.allowAddField && !isReadonly" size="small" type="primary" @click="addField(sec.__id)">新增字段</el-button>
        </div>

        <el-table :data="sec.fields" border size="small" class="mb8">
          <el-table-column type="index" width="50" />
          <el-table-column label="字段Key" min-width="100">
            <template #default="{ row }">
              <el-input v-model="row.key" :disabled="row.builtIn || isReadonly" size="small" placeholder="唯一键" />
            </template>
          </el-table-column>
          <el-table-column label="固定值否" width="100" align="center">
            <template #default="{ row }">
              <el-switch v-model="row.fixed" :disabled="row.builtIn || isReadonly" />
            </template>
          </el-table-column>
          <el-table-column label="字段中文名" min-width="140">
            <template #default="{ row }">
              <el-input v-model="row.nameCn" size="small" placeholder="必填" :disabled="isReadonly" />
            </template>
          </el-table-column>
          <el-table-column label="字段英文名" min-width="140">
            <template #default="{ row }">
              <el-input v-model="row.nameEn" size="small" placeholder="英文名" :disabled="isReadonly" />
            </template>
          </el-table-column>
          <el-table-column label="字段越南名" min-width="140">
            <template #default="{ row }">
              <el-input v-model="row.nameVn" size="small" placeholder="越南名" :disabled="isReadonly" />
            </template>
          </el-table-column>
          <el-table-column label="是否自动计算" width="120" align="center">
            <template #default="{ row }">
              <el-switch v-model="row.autoFill" :disabled="isReadonly" @change="onAutoFillChange(row)" />
            </template>
          </el-table-column>
          <el-table-column label="采购必填" width="100">
            <template #default="{ row }">
              <el-switch v-model="row.purchaserRequired" :disabled="isReadonly || row.autoFill" @change="onPurchaserRequiredChange(row)" />
            </template>
          </el-table-column>
          <el-table-column label="供应商操作" width="170">
            <template #default="{ row }">
              <el-select v-model="row.supplierBehavior" size="small" class="w-full" :disabled="isReadonly || row.autoFill" placeholder=" ">
                <el-option
                  v-for="opt in supplierBehaviorOptions(row.purchaserRequired, row.autoFill)"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="备注" min-width="160">
            <template #default="{ row }">
              <el-input v-model="row.remark" size="small" placeholder="备注说明" :disabled="isReadonly" />
            </template>
          </el-table-column>
          <el-table-column label="移除" width="80" align="center" fixed="right">
            <template #default="{ row }">
              <el-button
                v-if="!isReadonly && !row.builtIn"
                type="danger"
                link
                size="small"
                @click="removeField(sec, row)"
              >
                移除
              </el-button>
              <span v-else class="remove-col-placeholder">—</span>
            </template>
          </el-table-column>
        </el-table>

      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, reactive, ref, useAttrs, watch } from 'vue'

type SupplierBehavior =
  | ''
  | 'prefill_locked'
  | 'prefill_editable'
  | 'hidden_required'
  | 'hidden_optional'
  | 'required'
  | 'optional'

type FieldRow = {
  __id: string
  id?: string | number
  label: string
  nameCn: string
  nameEn: string
  nameVn: string
  key: string
  type: string
  fixed: boolean
  autoFill: boolean
  formula?: string
  purchaserRequired: boolean
  supplierRequiredCode?: number
  supplierBehavior: SupplierBehavior
  remark?: string
  builtIn?: boolean
  /** 明细行版本；未填时提交端按主表版本写入 */
  version?: number | null
}

type SectionRow = {
  __id: string
  id?: string | number
  title: string
  enabled?: boolean
  supplierCanAddRow: boolean
  allowAddField: boolean
  fields: FieldRow[]
}

const supplierBehaviorOptionsWhenPurchaserRequired: Array<{ label: string; value: SupplierBehavior }> = [
  { value: 'prefill_locked', label: '带出不可改' },
  { value: 'prefill_editable', label: '带出可改' },
  { value: 'hidden_required', label: '不带出必填' },
  { value: 'hidden_optional', label: '不带出可空' }
]

const supplierBehaviorOptionsWhenPurchaserNotRequired: Array<{ label: string; value: SupplierBehavior }> = [
  { value: 'required', label: '必填' },
  { value: 'optional', label: '可空' }
]

const blankSupplierBehaviorOption: Array<{ label: string; value: SupplierBehavior }> = [{ value: '', label: ' ' }]

const supplierBehaviorOptions = (purchaserRequired: boolean, autoFill = false) =>
  autoFill
    ? blankSupplierBehaviorOption
    : purchaserRequired
      ? supplierBehaviorOptionsWhenPurchaserRequired
      : supplierBehaviorOptionsWhenPurchaserNotRequired

const supplierBehaviorCodeMap: Record<SupplierBehavior, number> = {
  '': 0,
  prefill_locked: 1,
  prefill_editable: 2,
  hidden_required: 3,
  hidden_optional: 4,
  required: 5,
  optional: 6
}

const normalizeSupplierBehavior = (purchaserRequired: boolean, value?: SupplierBehavior): SupplierBehavior => {
  const allowedWhenRequired: SupplierBehavior[] = ['prefill_locked', 'prefill_editable', 'hidden_required', 'hidden_optional']
  const allowedWhenOptional: SupplierBehavior[] = ['required', 'optional']
  if (!value) return ''
  if (purchaserRequired) {
    return allowedWhenRequired.includes(value as SupplierBehavior) ? (value as SupplierBehavior) : 'prefill_locked'
  }
  return allowedWhenOptional.includes(value as SupplierBehavior) ? (value as SupplierBehavior) : 'optional'
}

const deriveSupplierBehavior = (
  purchaserRequired: boolean,
  supplierRequired: boolean,
  supplierEditable: boolean
): SupplierBehavior => {
  if (purchaserRequired) {
    if (supplierRequired && !supplierEditable) return 'prefill_locked'
    if (supplierRequired && supplierEditable) return 'prefill_editable'
    if (!supplierRequired && !supplierEditable) return 'hidden_required'
    return 'hidden_optional'
  }
  return supplierRequired ? 'required' : 'optional'
}

const supplierBehaviorFromRaw = (raw: any, purchaserRequired: boolean): SupplierBehavior => {
  const autoFill = raw?.autoFill === true || Number(raw?.is_computed ?? raw?.isComputed ?? 0) === 1
  if (autoFill) return ''
  const direct = raw?.supplierBehavior as SupplierBehavior | undefined
  if (direct) {
    return normalizeSupplierBehavior(purchaserRequired, direct)
  }
  const code = Number(raw?.supplier_required ?? raw?.supplierRequiredCode)
  if (Number.isInteger(code) && code >= 1 && code <= 6) {
    const matched = (Object.keys(supplierBehaviorCodeMap) as SupplierBehavior[]).find((key) => supplierBehaviorCodeMap[key] === code)
    return normalizeSupplierBehavior(purchaserRequired, matched)
  }
  return normalizeSupplierBehavior(
    purchaserRequired,
    deriveSupplierBehavior(purchaserRequired, !!raw?.supplierRequired, raw?.supplierEditable !== false)
  )
}

const syncComputedFieldState = (row: FieldRow) => {
  if (row.autoFill) {
    row.purchaserRequired = false
    row.supplierRequiredCode = 0
    row.supplierBehavior = ''
    return
  }
  row.supplierBehavior = row.supplierBehavior ? normalizeSupplierBehavior(row.purchaserRequired, row.supplierBehavior) : 'optional'
  row.supplierRequiredCode = supplierBehaviorCodeMap[row.supplierBehavior] || 0
}

const props = defineProps<{
  modelValue: any
  hideTitle?: boolean
  title?: string
  showTitleInput?: boolean
  defaultSections?: any[]
  visibleTitles?: string[]
  onDraftChange?: (sections: any[]) => void
  readonly?: boolean
}>()
const emit = defineEmits<{ (e: 'update:modelValue', v: any): void }>()
const attrs = useAttrs()

const titleText = computed(() => props.title || '结构配置')
const hideTitle = computed(() => props.hideTitle === true)
const showTitleInput = computed(() => props.showTitleInput !== false)
const isReadonly = computed(() => {
  if (props.readonly === true) return true
  return attrs.disabled !== undefined || attrs.readonly !== undefined
})
const canToggleSupplierAdd = (sec: SectionRow) => ['材料成本', '加工成本'].includes(sec.title)
const visibleAllowList = computed(() => {
  if (props.visibleTitles && props.visibleTitles.length) return props.visibleTitles.map((t) => t || '')
  const mv = props.modelValue as any
  if (Array.isArray(mv) && mv.length) {
    const enabledTitles = mv.filter((s: any) => s && s.enabled !== false).map((s: any) => s.title || '')
    if (enabledTitles.length) return enabledTitles
  }
  const embedded = (props.modelValue as any)?.__visibleTitles || []
  if (Array.isArray(embedded) && embedded.length) return embedded.map((t: string) => t || '')
  // Fallback for brand-new form: misc + BOM default tabs
  return ['材料成本', '加工成本', '其它成本', '利润', '税金']
})

const makeSyncKey = (list: SectionRow[]) =>
  JSON.stringify(
    list.map((s) => ({
      title: s.title,
      enabled: s.enabled !== false,
      supplierCanAddRow: !!s.supplierCanAddRow,
      allowAddField: !!s.allowAddField,
      fields: (s.fields || []).map((f) => ({
        key: f.key,
        label: f.label,
        nameCn: f.nameCn,
        nameEn: f.nameEn,
        nameVn: f.nameVn,
        type: f.type,
        fixed: !!f.fixed,
        autoFill: !!f.autoFill,
        purchaserRequired: !!f.purchaserRequired,
        supplierBehavior: f.supplierBehavior,
        remark: f.remark || ''
      }))
    }))
  )

let lastSyncKey = ''
/** 本组件 emit 后父级会回写 modelValue；跳过等量次数的 props 同步，避免每次按键都 syncFromProps 整表重建 */
let pendingParentEchoSkips = 0

const visibleSections = computed(() => {
  const allowList = visibleAllowList.value
  return allowList.length
    ? localSections.filter((s) => allowList.includes(s.title))
    : localSections.filter((s) => s.enabled !== false)
})

const active = ref('')
const localSections = reactive<SectionRow[]>([])
let syncing = false

const newId = () => {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID()
  }
  // Fallback for environments without randomUUID (e.g., older browsers or http contexts)
  return 'id-' + Math.random().toString(16).slice(2) + '-' + Date.now().toString(16)
}

const toFieldRow = (raw: any): FieldRow => {
  const builtIn = !!raw?.builtIn
  const fixed = raw?.fixed !== undefined ? !!raw.fixed : builtIn
  const row: FieldRow = {
    __id: raw?.__id || raw?.id || newId(),
    id: raw?.id,
    label: raw?.label || raw?.name || '',
    nameCn: raw?.nameCn || raw?.label || raw?.name || '',
    nameEn: raw?.nameEn || raw?.labelEn || '',
    nameVn: raw?.nameVn || raw?.labelVn || '',
    key: raw?.key || '',
    type: (raw?.type as string) || 'text',
    fixed,
    autoFill: raw?.autoFill === undefined ? !!raw?.formula : !!raw?.autoFill,
    formula: raw?.formula || '',
    purchaserRequired: !!raw?.purchaserRequired,
    supplierRequiredCode: Number(raw?.supplier_required ?? raw?.supplierRequiredCode ?? 0) || 0,
    supplierBehavior: supplierBehaviorFromRaw(raw, !!raw?.purchaserRequired),
    remark: raw?.remark || '',
    builtIn,
    version: raw?.version != null && raw?.version !== '' ? Number(raw.version) : undefined
  }
  syncComputedFieldState(row)
  return row
}

const isCostSection = (title: string) => ['材料成本', '加工成本'].includes(title)

const toSectionRow = (raw: any): SectionRow => {
  const title = raw?.title || raw?.name || ''
  const allowAddField = raw?.allowAddField !== false || isCostSection(title)
  return {
    __id: raw?.__id || raw?.id || newId(),
    id: raw?.id,
    title,
    enabled: raw?.enabled,
    supplierCanAddRow: raw?.supplierCanAddRow !== false,
    allowAddField,
    fields: Array.isArray(raw?.fields) ? raw.fields.map(toFieldRow) : []
  }
}

const syncFromProps = (val: any) => {
  syncing = true
  const incoming = Array.isArray(val) ? val : []
  const fallback = Array.isArray(props.defaultSections) ? props.defaultSections : []
  const source = incoming.length ? incoming : fallback
  const nextSections = source.map((s: any) => toSectionRow(s))
  const nextKey = makeSyncKey(nextSections)
  if (nextKey === lastSyncKey && localSections.length) {
    syncing = false
    return
  }
  lastSyncKey = nextKey
  localSections.splice(0, localSections.length)
  nextSections.forEach((s) => localSections.push(s))
  const firstVisible = visibleSections.value[0]?.__id
  if (!active.value || !visibleSections.value.find((s) => s.__id === active.value)) {
    active.value = firstVisible || localSections[0]?.__id || ''
  }
  syncing = false
}

watch(
  () => props.modelValue,
  (val) => {
    if (pendingParentEchoSkips > 0) {
      pendingParentEchoSkips -= 1
      return
    }
    syncFromProps(val)
  },
  { immediate: true, deep: true }
)

const flushEmitChange = () => {
  pendingParentEchoSkips += 1
  const allowList = visibleAllowList.value
  const clean = localSections.map((s) => ({
    id: s.id,
    name: s.title,
    title: s.title,
    enabled: allowList.length ? allowList.includes(s.title) : s.enabled !== false,
    supplierCanAddRow: s.supplierCanAddRow,
    allowAddField: s.allowAddField,
    fields: s.fields.map((f) => ({
      id: f.id,
      label: f.nameCn || f.label,
      nameCn: f.nameCn,
      nameEn: f.nameEn,
      nameVn: f.nameVn,
      key: f.key,
      type: f.type,
      fixed: !!f.fixed,
      autoFill: !!f.autoFill,
      formula: f.formula,
      purchaserRequired: f.autoFill ? false : f.purchaserRequired,
      supplierRequiredCode: f.autoFill ? 0 : supplierBehaviorCodeMap[f.supplierBehavior] || 0,
      supplier_required: f.autoFill ? 0 : supplierBehaviorCodeMap[f.supplierBehavior] || 0,
      supplierRequired: f.supplierBehavior === 'required' || f.supplierBehavior === 'prefill_locked' || f.supplierBehavior === 'prefill_editable',
      supplierEditable:
        f.supplierBehavior === 'optional' ||
        f.supplierBehavior === 'prefill_editable' ||
        f.supplierBehavior === 'hidden_optional',
      supplierBehavior: f.autoFill ? '' : f.supplierBehavior,
      remark: f.remark,
      builtIn: f.builtIn,
      ...(f.version != null ? { version: Number(f.version) } : {})
    }))
  }))
  ;(clean as any).__visibleTitles = allowList
  props.onDraftChange && props.onDraftChange(clean)
  emit('update:modelValue', clean)
}

let emitChangeQueued = false
const emitChange = () => {
  if (emitChangeQueued) return
  emitChangeQueued = true
  nextTick(() => {
    emitChangeQueued = false
    flushEmitChange()
  })
}

const addSection = () => {
  const id = newId()
  localSections.push({
    __id: id,
    title: '新分段',
    enabled: true,
    supplierCanAddRow: true,
    allowAddField: true,
    fields: []
  })
  active.value = id
}

const removeField = (section: SectionRow, row: FieldRow) => {
  if (isReadonly.value || row.builtIn) return
  const sec = localSections.find((s) => s.__id === section.__id)
  if (!sec) return
  const idx = sec.fields.findIndex((f) => f.__id === row.__id)
  if (idx >= 0) sec.fields.splice(idx, 1)
}

const addField = (sectionId: string) => {
  const sec = localSections.find((s) => s.__id === sectionId)
  if (!sec || !sec.allowAddField) return
  sec.fields.push({
    __id: newId(),
    label: '',
    nameCn: '',
    nameEn: '',
    nameVn: '',
    key: '',
    type: 'text',
    fixed: false,
    autoFill: false,
    formula: '',
    purchaserRequired: false,
    supplierBehavior: 'optional',
    remark: '',
    builtIn: false
  })
}

const onPurchaserRequiredChange = (row: FieldRow) => {
  if (row.autoFill) return
  row.supplierBehavior = row.purchaserRequired
    ? row.supplierBehavior === 'required'
      ? 'hidden_required'
      : row.supplierBehavior === 'optional'
        ? 'hidden_optional'
        : normalizeSupplierBehavior(true, row.supplierBehavior)
    : row.supplierBehavior === 'hidden_required'
      ? 'required'
      : row.supplierBehavior === 'hidden_optional'
        ? 'optional'
        : normalizeSupplierBehavior(false, row.supplierBehavior)
}

const onAutoFillChange = (row: FieldRow) => {
  row.autoFill = !!row.autoFill
  syncComputedFieldState(row)
}

watch(
  () => localSections,
  () => {
    if (!syncing && !isReadonly.value) emitChange()
  },
  { deep: true, flush: 'post' }
)
</script>

<style scoped>
.section-builder {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.title {
  font-weight: 600;
}
.title-spacer {
  flex: 1;
}
.pane-header {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 8px;
}
.flex-spacer { flex: 1; }
.w-220 { width: 220px; }
.w-full { width: 100%; }
.mb8 { margin-bottom: 8px; }
.remove-col-placeholder {
  color: var(--el-text-color-placeholder);
  font-size: 12px;
}
.tab-label { color: #6b7280; }
.tab-label--on { color: #16a34a; font-weight: 600; }
:global(.fc-section-item > .el-form-item__label) { display: none !important; }
:global(.fc-section-item > .el-form-item__content) { margin-left: 0 !important; }
:global(.price-template-fs-dialog .el-dialog) {
  width: 95vw !important;
  max-width: 1440px;
  min-width: 860px;
}
:global(.price-template-fs-dialog .el-dialog__body) {
  max-height: calc(90vh - 140px);
  overflow: auto;
}
</style>
