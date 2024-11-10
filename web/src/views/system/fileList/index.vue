<template>
  <fs-page>
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
    </fs-crud>
    <FileSelector ref="fileSelectorRef" :tabsShow="SHOW.ALL" :itemSize="120" :multiple="false" :selectable="false" />
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
}
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

// 页面打开后获取列表数据
onMounted(() => {
  crudExpose.doRefresh();
});
</script>