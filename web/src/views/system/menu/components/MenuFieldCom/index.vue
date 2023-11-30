<template>
  <div>
    <el-dialog ref="modelRef" v-model="modelDialog" title="选择model">
      <div v-show="props.model">
        <el-tag>已选择:{{ props.model }}</el-tag>
      </div>
      <div class="model-card">
        <div v-for="(item,index) in allModelData" :value="item.key" :key="index">
          <el-text :type="modelCheckIndex===index?'primary':''" @click="onModelChecked(item,index)">
            {{ item.app + '--' + item.title + '(' + item.key + ')' }}
          </el-text>
        </div>
      </div>
      <template #footer>
      <span class="dialog-footer">
        <el-button @click="modelDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAutomatch">
          确定
        </el-button>
      </span>
      </template>
    </el-dialog>
    <div style="height: 80vh">
      <fs-crud ref="crudRef" v-bind="crudBinding">
      </fs-crud>

    </div>
  </div>
</template>

<script lang="ts" setup>
import {ref, onMounted, reactive} from 'vue';
import {useFs} from '@fast-crud/fast-crud';
import {createCrudOptions} from './crud';
import {getModelList} from './api'
import {MenuTreeItemType} from "/@/views/system/menu/types";
import {successMessage, successNotification, warningNotification} from '/@/utils/message';
import {automatchColumnsData} from '/@/views/system/columns/components/ColumnsTableCom/api';
// 当前选择的菜单信息
let selectOptions: any = ref({name: null});

const props = reactive({
  model: '',
  app: '',
  menu: ''
})

//model弹窗
const modelDialog = ref(false)
// 获取所有model
const allModelData = ref<any[]>([]);
const modelCheckIndex = ref(null)
const onModelChecked = (row, index) => {
  modelCheckIndex.value = index
  props.model = row.key
  props.app = row.app
}
/**
 * 菜单选中时,加载表格数据
 * @param record
 */
const handleRefreshTable = (record: MenuTreeItemType) => {
  if (!record.is_catalog && record.id) {
    selectOptions.value = record;
    crudExpose.doRefresh();
  } else {
    //清空表格数据
    crudExpose.setTableData([]);
  }
};
/**
 * 自动匹配列
 */
const handleAutomatch = async () => {
  props.menu = selectOptions.value.id
  modelDialog.value = false
  if (props.menu && props.model) {
    const res = await automatchColumnsData(props);
    if (res?.code === 2000) {
      successNotification('匹配成功');
    }
    crudExpose.doSearch({form: {menu: props.menu, model: props.model}});
  }else {
    warningNotification('请选择角色和模型表！');
  }

};


const {crudBinding, crudRef, crudExpose} = useFs({createCrudOptions, props, modelDialog, selectOptions,allModelData});
onMounted(async () => {
  const res = await getModelList();
  allModelData.value = res.data;
});

defineExpose({selectOptions, handleRefreshTable});
</script>

<style scoped lang="scss">
.model-card {
  margin-top: 10px;
  height: 30vh;
  overflow-y: scroll;

  div {
    margin: 15px 0;
    cursor: pointer;
  }
}
</style>
