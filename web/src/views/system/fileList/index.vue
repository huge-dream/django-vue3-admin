<template>
  <fs-page>
    <FileSelector v-model="selected" :showInput="false" ref="fileSelectorRef" :tabsShow="SHOW.ALL" :itemSize="120"
      :multiple="false" :selectable="true" valueKey="url" inputType="image">
      <!-- <template #input="scope">
        input：{{ scope }}
      </template> -->
      <!-- <template #actionbar-left="scope">
        actionbar-left：{{ scope }}
      </template> -->
      <!-- <template #actionbar-right="scope">
        actionbar-right：{{ scope }}
      </template> -->
      <!-- <template #empty="scope">
        empty：{{ scope }}
      </template> -->
      <!-- <template #item="{ data }">
        {{ data }}
      </template> -->
    </FileSelector>
    <fs-crud ref="crudRef" v-bind="crudBinding">
      <template #actionbar-left="scope">
        <el-upload :action="getBaseURL() + 'api/system/file/'" :multiple="false"
          :on-success="() => crudExpose.doRefresh()" :drag="false" :show-file-list="false">
          <el-button type="primary" icon="plus">上传</el-button>
        </el-upload>
      </template>
      <template #cell_size="scope">
        <span>{{ scope.row.size ? getSizeDisplay(scope.row.size) : '0b' }}</span>
      </template>
      <template #cell_preview="scope">
        <div v-if="scope.row.file_type === 0">
          <el-image style="width: 100%; aspect-ratio: 1 /1 ;" :src="getBaseURL(scope.row.url)"
            :preview-src-list="[getBaseURL(scope.row.url)]" :preview-teleported="true" />
        </div>
        <div v-if="scope.row.file_type === 1" class="_preview"
          @click="openPreviewHandle(getBaseURL(scope.row.url), 'video')">
          <el-icon :size="60">
            <VideoCamera />
          </el-icon>
        </div>
        <div v-if="scope.row.file_type === 2" class="_preview"
          @click="openPreviewHandle(getBaseURL(scope.row.url), 'video')">
          <el-icon :size="60">
            <Headset />
          </el-icon>
        </div>
        <el-icon v-if="scope.row.file_type === 3" :size="60">
          <Document />
        </el-icon>
        <div v-if="scope.row.file_type > 3">未知类型</div>
      </template>
    </fs-crud>
    <div class="preview" :class="{ show: openPreview }">
      <video v-show="videoPreviewSrc" :src="videoPreviewSrc" class="previewItem" :controls="true" :autoplay="true"
        :muted="true" :loop="false" ref="videoPreviewRef"></video>
      <audio v-show="audioPreviewSrc" :src="audioPreviewSrc" class="previewItem" :controls="true" :autoplay="false"
        :muted="true" :loop="false" ref="audioPreviewRef"></audio>
      <div class="closePreviewBtn">
        <el-icon :size="48" color="white" style="cursor: pointer;" @click="closePreview">
          <CircleClose />
        </el-icon>
      </div>
    </div>
  </fs-page>
</template>

<script lang="ts" setup>
import { ref, onMounted, nextTick } from 'vue';
import { useExpose, useCrud } from '@fast-crud/fast-crud';
import { createCrudOptions } from './crud';
import { getBaseURL } from '/@/utils/baseUrl';
import FileSelector from '/@/components/fileSelector/index.vue';
import { SHOW } from '/@/components/fileSelector/types';

const fileSelectorRef = ref<any>(null);
const getSizeDisplay = (n: number) => n < 1024 ? n + 'b' : (n < 1024 * 1024 ? (n / 1024).toFixed(2) + 'Kb' : (n / (1024 * 1024)).toFixed(2) + 'Mb');

const openAddHandle = async () => {
  fileSelectorRef.value.selectVisiable = true;
  await nextTick();
};
// crud组件的ref
const crudRef = ref();
// crud 配置的ref
const crudBinding = ref();
// 暴露的方法
const { crudExpose } = useExpose({ crudRef, crudBinding });
// 你的crud配置
const { crudOptions } = createCrudOptions({ crudExpose, context: { openAddHandle } });
// 初始化crud配置
const { resetCrudOptions } = useCrud({ crudExpose, crudOptions });

const selected = ref<any>([]);
const openPreview = ref<boolean>(false);
const videoPreviewSrc = ref<string>('');
const audioPreviewSrc = ref<string>('');
const videoPreviewRef = ref<HTMLVideoElement>();
const audioPreviewRef = ref<HTMLAudioElement>();
const openPreviewHandle = (src: string, type: string) => {
  openPreview.value = true;
  (videoPreviewRef.value as HTMLVideoElement).muted = true;
  (audioPreviewRef.value as HTMLAudioElement).muted = true;
  if (type === 'video') videoPreviewSrc.value = src;
  else audioPreviewSrc.value = src;
  window.addEventListener('keydown', onPreviewKeydown);
};
const closePreview = () => {
  openPreview.value = false;
  videoPreviewSrc.value = '';
  audioPreviewSrc.value = '';
  window.removeEventListener('keydown', onPreviewKeydown);
};
const onPreviewKeydown = (e: KeyboardEvent) => {
  if (e.key !== 'Escape') return;
  openPreview.value = false;
  videoPreviewSrc.value = '';
  audioPreviewSrc.value = '';
  window.removeEventListener('keydown', onPreviewKeydown);
};

// 页面打开后获取列表数据
onMounted(() => {
  crudExpose.doRefresh();
});
</script>
<style lang="css" scoped>
.preview {
  display: none;
  position: fixed;
  top: 0;
  height: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, .5);
  z-index: 9999;
}

.show {
  display: block !important;
}

.previewItem {
  width: 50%;
  position: absolute;
  top: 50%;
  right: 50%;
  transform: translate(25%, -50%);
}

.closePreviewBtn {
  width: 50%;
  position: absolute;
  bottom: 10%;
  left: 50%;
  transform: translate(-75%);
  display: flex;
  justify-content: center;
}

._preview {
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
}
</style>