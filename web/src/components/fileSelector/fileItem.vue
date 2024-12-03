<template>
    <div ref="itemRef" class="file-item" :title="data.name" @mouseenter="isShow = true" @mouseleave="isShow = false">
        <div class="file-name" :class="{ show: isShow }">{{ data.name }}</div>
        <component :is="FileTypes[data.file_type].tag" v-bind="FileTypes[data.file_type].attr" />
    </div>
</template>
<script setup lang="ts">
import { defineComponent, nextTick } from 'vue';
import { ref, defineProps, PropType, watch, onMounted, h } from 'vue';
const props = defineProps({
    fileData: { type: Object as PropType<any>, required: true },
});
const _OtherFileComponent = defineComponent({ template: '<el-icon><Files /></el-icon>' });
const FileTypes = [
    { tag: 'img', attr: { src: props.fileData.url, draggable: false } },
    { tag: 'video', attr: { src: props.fileData.url, controls: false, autoplay: true, muted: true, loop: true } },
    { tag: 'audio', attr: { src: props.fileData.url, controls: true, autoplay: false, muted: false, loop: false, volume: 0 } },
    { tag: _OtherFileComponent, attr: { style: { fontSize: '2rem' } } },
];
const isShow = ref<boolean>(false);
const itemRef = ref<HTMLDivElement | null>(null);
const data = ref<any>(null);
watch(props.fileData, (nVal) => data.value = nVal, { immediate: true, deep: true });
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

.show {
    display: flex !important;
}
</style>