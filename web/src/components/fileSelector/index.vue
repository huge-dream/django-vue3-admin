<template>
  <div style="width: 100%;" :class="props.class" :style="props.style">
    <slot name="input" v-bind="{}">
      <div v-if="props.showInput" style="width: 100%;" :class="props.inputClass" :style="props.inputStyle">
        <el-select v-if="props.inputType === 'selector'" v-model="data" suffix-icon="arrow-down" clearable
          :multiple="props.multiple" placeholder="请选择文件" @click="selectVisiable = true && !props.disabled"
          :disabled="props.disabled" @clear="selectedInit" @remove-tag="selectedInit">
          <el-option v-for="item, index in listAllData" :key="index" :value="String(item[props.valueKey])"
            :label="item.name" />
        </el-select>

        <div v-if="props.inputType === 'image' && props.multiple"
          style="width: 100%; display: flex; gap: 4px; flex-wrap: wrap; margin-bottom: 4px;">
          <div v-for="item, index in (data || [])" style="position: relative;"
            :style="{ width: props.inputSize + 'px', height: props.inputSize + 'px' }">
            <el-image :src="item" :key="index" fit="scale-down" class="itemList"
              :style="{ width: props.inputSize + 'px', aspectRatio: '1 / 1' }" />
            <el-icon v-show="(!!data && !props.disabled)" class="closeHover" :size="16" @click="clearOne(item)">
              <Close />
            </el-icon>
          </div>
          <div style="position: relative;" :style="{ width: props.inputSize + 'px', height: props.inputSize + 'px' }">
            <div
              style="position: absolute; left: 0; top: 0; width: 100%; height: 100%; display: flex; justify-content: center; align-items: center;">
              <el-icon :size="24">
                <Plus />
              </el-icon>
            </div>
            <div @click="selectVisiable = true && !props.disabled" class="addControllorHover"
              :style="{ cursor: props.disabled ? 'not-allowed' : 'pointer' }"></div>
          </div>
        </div>
        <div v-if="props.inputType === 'image' && !props.multiple" class="form-display" style="position: relative;"
          @mouseenter="formDisplayEnter" @mouseleave="formDisplayLeave"
          :style="{ width: props.inputSize + 'px', height: props.inputSize + 'px' }">
          <el-image :src="data" fit="scale-down" :style="{ width: props.inputSize + 'px', aspectRatio: '1 / 1' }">
            <template #error>
              <div></div>
            </template>
          </el-image>
          <div v-show="!(!!data)"
            style="position: absolute; left: 0; top: 0; width: 100%; height: 100%; display: flex; justify-content: center; align-items: center;">
            <el-icon :size="24">
              <Plus />
            </el-icon>
          </div>
          <div @click="selectVisiable = true && !props.disabled" class="addControllorHover"
            :style="{ cursor: props.disabled ? 'not-allowed' : 'pointer' }"></div>
          <el-icon v-show="(!!data && !props.disabled) && !props.multiple" class="closeHover" :size="16" @click="clear">
            <Close />
          </el-icon>
        </div>

        <div v-if="props.inputType === 'video'" class="form-display" @mouseenter="formDisplayEnter"
          @mouseleave="formDisplayLeave"
          style="position: relative; display: flex; align-items: center;  justify-items: center;"
          :style="{ width: props.inputSize * 2 + 'px', height: props.inputSize + 'px' }">
          <video :src="data" :controls="false" :autoplay="true" :muted="true" :loop="true"
            :style="{ maxWidth: props.inputSize * 2 + 'px', maxHeight: props.inputSize + 'px', margin: '0 auto' }"></video>
          <div v-show="!(!!data)"
            style="position: absolute; left: 0; top: 0; width: 100%; height: 100%; display: flex; justify-content: center; align-items: center;">
            <el-icon :size="24">
              <Plus />
            </el-icon>
          </div>
          <div @click="selectVisiable = true && !props.disabled" class="addControllorHover"
            :style="{ cursor: props.disabled ? 'not-allowed' : 'pointer' }"></div>
          <el-icon v-show="!!data && !props.disabled" class="closeHover" :size="16" @click="clear">
            <Close />
          </el-icon>
        </div>

        <div v-if="props.inputType === 'audio'" class="form-display" @mouseenter="formDisplayEnter"
          @mouseleave="formDisplayLeave"
          style="position: relative; display: flex; align-items: center;  justify-items: center;"
          :style="{ width: props.inputSize * 2 + 'px', height: props.inputSize + 'px' }">
          <audio :src="data" :controls="!!data" :autoplay="false" :muted="true" :loop="true"
            style="width: 100%; z-index: 1;"></audio>
          <div v-show="!(!!data)"
            style="position: absolute; left: 0; top: 0; width: 100%; height: 100%; display: flex; justify-content: center; align-items: center;">
            <el-icon :size="24">
              <Plus />
            </el-icon>
          </div>
          <div @click="selectVisiable = true && !props.disabled" class="addControllorHover"
            :style="{ cursor: props.disabled ? 'not-allowed' : 'pointer' }"></div>
          <el-icon v-show="!!data && !props.disabled" class="closeHover" :size="16" @click="clear">
            <Close />
          </el-icon>
        </div>
      </div>
    </slot>
    <el-dialog v-model="selectVisiable" :draggable="true" width="50%" :align-center="false" :append-to-body="true"
      @open="if (listData.length === 0) listRequest();" @close="onClose" @closed="onClosed" modal-class="_overlay">
      <template #header>
        <span class="el-dialog__title">文件选择</span>
        <el-divider style="margin: 0;" />
      </template>
      <div style="padding: 4px;">
        <div style="width: 100%; display: flex; justify-content: space-between; gap: 12px;">
          <el-tabs style="width: 100%;" v-model="tabsActived" :type="props.tabsType" :stretch="true"
            @tab-change="handleTabChange" v-if="!isSuperTenent">
            <el-tab-pane v-if="props.tabsShow & SHOW.IMAGE" :name="0" label="图片" />
            <el-tab-pane v-if="props.tabsShow & SHOW.VIDEO" :name="1" label="视频" />
            <el-tab-pane v-if="props.tabsShow & SHOW.AUDIO" :name="2" label="音频" />
            <el-tab-pane v-if="props.tabsShow & SHOW.OTHER" :name="3" label="其他" />
          </el-tabs>
          <el-tabs style="width: 100%;" v-model="tabsActived" :type="props.tabsType" :stretch="true"
            @tab-change="handleTabChange" v-if="isTenentMode">
            <el-tab-pane v-if="props.tabsShow & SHOW.IMAGE" :name="4" label="系统图片" />
            <el-tab-pane v-if="props.tabsShow & SHOW.VIDEO" :name="5" label="系统视频" />
            <el-tab-pane v-if="props.tabsShow & SHOW.AUDIO" :name="6" label="系统音频" />
            <el-tab-pane v-if="props.tabsShow & SHOW.OTHER" :name="7" label="系统其他" />
          </el-tabs>
        </div>
        <el-row justify="space-between" class="headerBar">
          <el-col :span="12">
            <slot name="actionbar-left">
              <el-input v-model="filterForm.name" :placeholder="`请输入${TypeLabel[tabsActived % 4]}名`"
                prefix-icon="search" clearable @change="listRequest" />
              <div>
                <el-tag v-if="props.multiple" type="primary" effect="light">
                  一共选中&nbsp;{{ data?.length || 0 }}&nbsp;个文件
                </el-tag>
              </div>
            </slot>
          </el-col>
          <el-col :span="12" style="width: 100%; display: flex; gap: 12px; justify-content: flex-end;">
            <slot name="actionbar-right" v-bind="{}">
              <el-button type="default" circle icon="refresh" @click="listRequest" />
              <template v-if="tabsActived > 3 ? isSuperTenent : true">
                <el-upload ref="uploadRef" :action="getBaseURL() + 'api/system/file/'" :multiple="false" :drag="false"
                  :data="{ upload_method: 1 }" :show-file-list="true" :accept="AcceptList[tabsActived % 4]"
                  :on-success="() => { listRequest(); listRequestAll(); uploadRef.clearFiles(); }"
                  v-if="props.showUploadButton">
                  <el-button type="primary" icon="plus">上传{{ TypeLabel[tabsActived % 4] }}</el-button>
                </el-upload>
                <el-button type="info" icon="link" @click="netVisiable = true" v-if="props.showNetButton">
                  网络{{ TypeLabel[tabsActived % 4] }}
                </el-button>
              </template>
            </slot>
          </el-col>
        </el-row>
        <div v-if="!listData.length">
          <slot name="empty">
            <el-empty description="无内容，请上传" style="width: 100%; height: calc(50vh); margin-top: 24px; padding: 4px;" />
          </slot>
        </div>
        <div ref="listContainerRef" class="listContainer" v-else>
          <div v-for="item, index in listData" :key="index" @click="onItemClick($event)" :data-id="item[props.valueKey]"
            :style="{ width: (props.itemSize || 100) + 'px', cursor: props.selectable ? 'pointer' : 'normal' }">
            <slot name="item" :data="item">
              <FileItem :fileData="item" :api="fileApi" :showClose="tabsActived < 4 || isSuperTenent"
                @onDelFile="listRequest(); listRequestAll();" />
            </slot>
          </div>
        </div>
        <div class="listPaginator">
          <el-pagination background size="small" layout="total, sizes, prev, pager, next" :total="pageForm.total"
            v-model:page-size="pageForm.limit" :page-sizes="[10, 20, 30, 40, 50]" v-model:current-page="pageForm.page"
            :hide-on-single-page="false" @change="handlePageChange" />
        </div>
      </div>
      <!-- 只要在获取中，就最大程度阻止关闭dialog -->
      <el-dialog v-model="netVisiable" :draggable="false" width="50%" :align-center="false" :append-to-body="true"
        :title="'网络' + TypeLabel[tabsActived % 4] + '上传'" @closed="netUrl = ''" :close-on-click-modal="!netLoading"
        :close-on-press-escape="!netLoading" :show-close="!netLoading" modal-class="_overlay">
        <el-form-item :label="TypeLabel[tabsActived % 4] + '链接'">
          <el-input v-model="netUrl" placeholder="请输入网络连接" clearable @input="netChange">
            <template #prepend>
              <el-select v-model="netPrefix" style="width: 110px;">
                <el-option v-for="item, index in ['HTTP://', 'HTTPS://']" :key="index" :label="item" :value="item" />
              </el-select>
            </template>
          </el-input>
        </el-form-item>
        <template #footer>
          <el-button v-if="!netLoading" type="default" @click="netVisiable = false">取消</el-button>
          <el-button type="primary" @click="confirmNetUrl" :loading="netLoading">
            {{ netLoading ? '网络文件获取中...' : '确定' }}
          </el-button>
        </template>
      </el-dialog>
      <template #footer v-if="props.showInput">
        <el-button type="default" @click="onClose">取消</el-button>
        <el-button type="primary" @click="onSave">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { useUi, UserPageQuery, AddReq, EditReq, DelReq } from '@fast-crud/fast-crud';
import { ref, reactive, defineProps, PropType, watch, onMounted, nextTick } from 'vue';
import { getBaseURL } from '/@/utils/baseUrl';
import { request } from '/@/utils/service';
import { SHOW } from './types';
import FileItem from './fileItem.vue';
import { pluginsAll } from '/@/views/plugins/index';
import { storeToRefs } from "pinia";
import { useUserInfo } from "/@/stores/userInfo";
import { errorNotification, successNotification } from '/@/utils/message';

const userInfos = storeToRefs(useUserInfo()).userInfos;
const isTenentMode = !!(pluginsAll && pluginsAll.length && pluginsAll.indexOf('dvadmin3-tenants-web') >= 0);
const isSuperTenent = (userInfos.value as any).schema_name === 'public';

const TypeLabel = ['图片', '视频', '音频', '文件']
const AcceptList = ['image/*', 'video/*', 'audio/*', ''];
const props = defineProps({
  modelValue: {},
  class: { type: Object as PropType<String | Object>, default: '' },
  inputClass: { type: Object as PropType<String | Object>, default: '' },
  style: { type: Object as PropType<Object | string>, default: {} },
  inputStyle: { type: Object as PropType<Object | string>, default: {} },
  disabled: { type: Boolean, default: false },

  tabsType: { type: Object as PropType<'' | 'card' | 'border-card'>, default: '' },
  itemSize: { type: Number, default: 100 },

  // 1000图片 100视频 10音频 1 其他 控制tabs的显示
  tabsShow: { type: Number, default: SHOW.ALL },

  // 是否可以多选，默认单选
  // 该值为true时inputType必须是selector或image（暂不支持其他type的多选）
  multiple: { type: Boolean, default: false },

  // 是否可选，该参数用于只上传和展示而不选择和绑定model的情况
  selectable: { type: Boolean, default: true },

  // 该参数用于控制是否显示表单item。若赋值为false，则不会显示表单item，也不会显示底部按钮
  // 如果不显示表单item，则无法触发dialog，需要父组件通过修改本组件暴露的 selectVisiable 状态来控制dialog
  showInput: { type: Boolean, default: true },

  // 表单item类型，不为selector是需要设置valueKey，否则可能获取不到媒体数据
  inputType: { type: Object as PropType<'selector' | 'image' | 'video' | 'audio'>, default: 'selector' },
  // inputType不为selector时生效
  inputSize: { type: Number, default: 100 },

  // v-model绑定的值是file数据的哪个key，默认是url
  valueKey: { type: String, default: 'url' },

  showUploadButton: { type: Boolean, default: true },
  showNetButton: { type: Boolean, default: true },
} as any);

const selectVisiable = ref<boolean>(false);
const tabsActived = ref<number>([3, 2, 1, 0][((props.tabsShow & (props.tabsShow - 1)) === 0) ? Math.log2(props.tabsShow) : 3]);
const fileApiPrefix = '/api/system/file/';
const fileApi = {
  GetList: (query: UserPageQuery) => request({ url: fileApiPrefix, method: 'get', params: query }),
  AddObj: (obj: AddReq) => request({ url: fileApiPrefix, method: 'post', data: obj }),
  DelObj: (id: DelReq) => request({ url: fileApiPrefix + id + '/', method: 'delete', data: { id } }),
  GetAll: () => request({ url: fileApiPrefix + 'get_all/' }),
};
// 过滤表单
const filterForm = reactive({ name: '' });
// 分页表单
const pageForm = reactive({ page: 1, limit: 10, total: 0 });
// 展示的数据列表
const listData = ref<any[]>([]);
const listAllData = ref<any[]>([]);
const listRequest = async () => {
  let res = await fileApi.GetList({
    page: pageForm.page,
    limit: pageForm.limit,
    file_type: isTenentMode ? tabsActived.value % 4 : tabsActived.value,
    system: tabsActived.value > 3,
    upload_method: 1,
    ...filterForm
  });
  listData.value = [];
  await nextTick();
  listData.value = (res.data as any[]).map((item: any) => ({ ...item, url: getBaseURL(item.url) }));
  pageForm.total = res.total;
  pageForm.page = res.page;
  pageForm.limit = res.limit;
  selectedInit();
};
const formDisplayEnter = (e: MouseEvent) => (e.target as HTMLElement).style.setProperty('--fileselector-close-display', 'block');
const formDisplayLeave = (e: MouseEvent) => (e.target as HTMLElement).style.setProperty('--fileselector-close-display', 'none');
const listRequestAll = async () => {
  if (props.inputType !== 'selector') return;
  let res = await fileApi.GetAll();
  listAllData.value = res.data;
};
// tab改变时触发
const handleTabChange = (name: string) => { pageForm.page = 1; listRequest(); };
// 分页器改变时触发
const handlePageChange = (currentPage: number, pageSize: number) => { pageForm.page = currentPage; pageForm.limit = pageSize; listRequest(); };
// 选择的行为
const listContainerRef = ref<any>();
const onItemClick = async (e: MouseEvent) => {
  if (!props.selectable) return;
  let target = e.target as HTMLElement;
  let flat = 0;  // -1删除 0不变 1添加
  while (!target.dataset.id) target = target.parentElement as HTMLElement;
  let fileId = target.dataset.id;
  if (props.multiple) {
    if (!!!data.value) data.value = [];
    if (target.classList.contains('active')) { target.classList.remove('active'); flat = -1; }
    else { target.classList.add('active'); flat = 1; }
    if (data.value.length) {
      let _l = JSON.parse(JSON.stringify(data.value));
      if (flat === 1) _l.push(fileId);
      else _l.splice(_l.indexOf(fileId), 1);
      data.value = _l;
    } else data.value = [fileId];
    // 去重排序，<降序，>升序
    data.value = Array.from(new Set(data.value)).sort();
  } else {
    for (let i of listContainerRef.value?.children) (i as HTMLElement).classList.remove('active');
    target.classList.add('active');
    data.value = fileId;
  }
  // onDataChange(data.value);
};
// 每次列表刷新都得更新一下选择状态，因为所有标签页共享列表
const selectedInit = async () => {
  if (!props.selectable) return;
  await nextTick(); // 不等待一次不会刷新
  for (let i of (listContainerRef.value?.children || [])) {
    i.classList.remove('active');
    let fid = (i as HTMLElement).dataset.id;
    if (props.multiple) { if (data.value?.includes(fid)) i.classList.add('active'); }
    else { if (fid === data.value) i.classList.add('active'); }
  }
};
const uploadRef = ref<any>();
const onSave = () => {
  onDataChange(data.value);
  emit('onSave', data.value);
  selectVisiable.value = false;
};
const onClose = () => {
  data.value = props.modelValue;
  emit('onClose');
  selectVisiable.value = false;
};
const onClosed = () => {
  clearState();
  emit('onClosed');
};
// 清空状态
const clearState = () => {
  filterForm.name = '';
  pageForm.page = 1;
  pageForm.limit = 10;
  pageForm.total = 0;
  listData.value = [];
  // all数据不能清，因为all只会在挂载的时候赋值一次
  // listAllData.value = [];
};
const clear = () => { data.value = null; onDataChange(null); };
const clearOne = (item: any) => {
  let _l = (JSON.parse(JSON.stringify(data.value)) as any[]).filter((i: any) => i !== item)
  data.value = _l;
  onDataChange(_l);
};

// 网络文件部分
const netLoading = ref<boolean>(false);
const netVisiable = ref<boolean>(false);
const netUrl = ref<string>('');
const netPrefix = ref<string>('HTTP://');
const netChange = () => {
  let s = netUrl.value.trim();
  if (s.toUpperCase().startsWith('HTTP://') || s.toUpperCase().startsWith('HTTPS://')) s = s.split('://')[1];
  if (s.startsWith('/')) s = s.substring(1);
  netUrl.value = s;
};
const confirmNetUrl = () => {
  if (!netUrl.value) return;
  netLoading.value = true;
  let controller = new AbortController();
  let timeout = setTimeout(() => {
    controller.abort();
  }, 10 * 1000);
  fetch(netPrefix.value + netUrl.value, { signal: controller.signal }).then(async (res: Response) => {
    clearTimeout(timeout);
    if (!res.ok) errorNotification(`网络${TypeLabel[tabsActived.value % 4]}获取失败！`);
    const _ = res.url.split('?')[0].split('/');
    let filename = _[_.length - 1];
    // let filetype = res.headers.get('content-type')?.split('/')[1] || '';
    let blob = await res.blob();
    let file = new File([blob], filename, { type: blob.type });
    let form = new FormData();
    form.append('file', file);
    form.append('upload_method', '1');
    fetch(getBaseURL() + 'api/system/file/', { method: 'post', body: form })
      .then(() => successNotification('网络文件上传成功！'))
      .then(() => { netVisiable.value = false; listRequest(); listRequestAll(); })
      .catch(() => errorNotification('网络文件上传失败！'))
      .then(() => netLoading.value = false);
  }).catch((err: any) => {
    console.log(err);
    clearTimeout(timeout);
    errorNotification(`网络${TypeLabel[tabsActived.value % 4]}获取失败！`);
    netLoading.value = false;
  });
};




// fs-crud部分
const data = ref<any>(null);
const emit = defineEmits(['update:modelValue', 'onSave', 'onClose', 'onClosed']);
watch(
  () => props.modelValue,
  (val) => data.value = props.multiple ? JSON.parse(JSON.stringify(val)) : val,
  { immediate: true }
);
const { ui } = useUi();
const formValidator = ui.formItem.injectFormItemContext();
const onDataChange = (value: any) => {
  let _v = null;
  if (value) {
    if (typeof value === 'string') _v = value.replace(/\\/g, '/');
    else {
      _v = [];
      for (let i of value) _v.push(i.replace(/\\/g, '/'));
    }
  }
  emit('update:modelValue', _v);
  formValidator.onChange();
  formValidator.onBlur();
};

defineExpose({ data, onDataChange, selectVisiable, clearState, clear });

onMounted(() => {

  if (props.multiple && !['selector', 'image'].includes(props.inputType))
    throw new Error('FileSelector组件属性multiple为true时inputType必须为selector');
  listRequestAll();
  console.log('fileselector tenentmdoe', isTenentMode);
  console.log('fileselector supertenent', isSuperTenent);
});
</script>

<style scoped>
.form-display {
  --fileselector-close-display: none;
  overflow: hidden;
}

._overlay {
  width: unset !important;
}

.headerBar>* {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

:deep(.el-input-group__prepend) {
  padding: 0 20px;
}

.listContainer {
  display: grid;
  justify-items: center;
  grid-template-columns: repeat(4, 1fr);
  grid-auto-rows: min-content;
  grid-gap: 36px;
  margin-top: 24px;
  padding: 8px;
  height: calc(50vh);
  overflow-y: auto;
  scrollbar-width: thin;
}

.listContainer>* {
  aspect-ratio: 1 / 1;
  box-shadow: 0 0 4px rgba(0, 0, 0, .2);
  border-radius: 8px;
  overflow: hidden;
}

.active {
  box-shadow: 0 0 8px var(--el-color-primary);
}

.listPaginator {
  display: flex;
  justify-content: flex-end;
  justify-items: center;
  padding-top: 24px;
}

.addControllorHover {
  width: 100%;
  height: 100%;
  position: absolute;
  left: 0;
  top: 0;
  cursor: pointer;
  border-radius: 8px;
  border: 1px solid #dcdfe6;
}

.addControllorHover:hover {
  border-color: #c0c4cc;
}

.closeHover {
  display: var(--fileselector-close-display);
  position: absolute;
  right: 2px;
  top: 2px;
  cursor: pointer;
}

.itemList {
  border: 1px solid #dcdfe6;
  border-radius: 8px;
}
</style>