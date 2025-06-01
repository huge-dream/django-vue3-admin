<template>
  <div ref="itemRef" class="file-item" :title="data.name" @mouseenter="isShow = true" @mouseleave="isShow = false">
    <div v-if="showTitle" class="file-name" :class="{ show: isShow }">{{ data.name }}</div>
    <component :is="FileTypes[data.file_type].tag" v-bind="FileTypes[data.file_type].attr" />
    <div v-if="props.showClose" class="file-del" :class="{ show: isShow }">
      <el-icon :size="24" color="white" @click.stop="delFileHandle" style="cursor: pointer;">
        <CircleClose style="mix-blend-mode: difference;" />
      </el-icon>
    </div>
  </div>
</template>
<script setup lang="ts">
import { defineComponent } from 'vue';
import { ref, defineProps, PropType, watch, onMounted, h } from 'vue';
import { successNotification } from '/@/utils/message';
import { getBaseURL } from '/@/utils/baseUrl';
const props = defineProps({
  fileData: { type: Object as PropType<any>, required: true },
  api: { type: Object as PropType<any>, required: true },
  showTitle: { type: Boolean, default: true },
  showClose: { type: Boolean, default: true },
});
const _OtherFileComponent = defineComponent({ template: '<el-icon><Files /></el-icon>' });
const FileTypes = [
  { tag: 'img', attr: { src: getBaseURL(props.fileData.url), draggable: false } },
  { tag: 'video', attr: { src: getBaseURL(props.fileData.url), controls: false, autoplay: true, muted: true, loop: true } },
  { tag: 'audio', attr: { src: getBaseURL(props.fileData.url), controls: true, autoplay: false, muted: false, loop: false, volume: 0 } },
  { tag: _OtherFileComponent, attr: { style: { fontSize: '2rem' } } },
];
const isShow = ref<boolean>(false);
const itemRef = ref<HTMLDivElement>();
const data = ref<any>(null);
const delFileHandle = () => props.api.DelObj(props.fileData.id).then(() => {
  successNotification('删除成功');
  emit('onDelFile');
});
watch(props.fileData, (nVal) => data.value = nVal, { immediate: true, deep: true });
const emit = defineEmits(['onDelFile']);
defineExpose({});
onMounted(() => { });
</script>
<style scoped>
.file-item {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-items: center;
}

.file-item>* {
  width: 100% !important;
}

.file-name {
  display: none;
  position: absolute;
  top: 0;
  left: 0;
  padding: 4px 12px;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
  word-break: break-all;
  white-space: normal;
  color: white;
  background-color: rgba(0, 0, 0, .5);
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-del {
  display: none;
  position: absolute;
  left: 0;
  bottom: 0;
  justify-content: flex-end;
}

.show {
  display: flex !important;
}
</style>