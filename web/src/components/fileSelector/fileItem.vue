<template>
    <div ref="itemRef" class="file-item" :title="data.name">
        <div class="file-name">{{ data.name }}</div>
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
const itemRef = ref<HTMLDivElement | null>(null);
const data = ref<any>(null);
watch(props.fileData, (nVal) => data.value = nVal, { immediate: true, deep: true });
defineExpose({});
onMounted(async () => {
    await nextTick();
    itemRef.value?.addEventListener('mouseenter', () => {
        itemRef.value?.querySelector('.file-name')?.classList.add('show');
    });
    itemRef.value?.addEventListener('mouseleave', () => {
        itemRef.value?.querySelector('.file-name')?.classList.remove('show');
    });
});
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
    padding: 0 12px;
    text-align: center;
    color: white;
    background-color: rgba(0, 0, 0, .5);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.show {
    display: block !important;
}
</style>