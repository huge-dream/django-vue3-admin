<template>
 <div>
   <el-divider>模型表</el-divider>
   <div class="model-card">
     <div v-for="(item,index) in allModelData" :key="index">
       <el-text @click="onModelChecked(item,index)" :type="modelCheckIndex===index?'primary':''">{{item.app + '--'+item.title + '('+item.key+')' }}</el-text>
     </div>
   </div>
   <el-divider>字段权限</el-divider>
   <div style="height: 50vh">
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
const propsContext = defineProps({
  roleId:{
    type:String||Number,
    required:true
  }
})

const props = reactive({
  role: '',
  model: '',
  app: '',
  menu:''
})



// 获取所有model
const allModelData = ref<any[]>([]);
const modelCheckIndex=ref(-1)
const onModelChecked = (row,index)=>{
  modelCheckIndex.value = index
  props.model = row.key
  props.app = row.app
  props.role=propsContext.roleId
  crudExpose.setTableData([])
  crudExpose.doSearch({form:{role:propsContext.roleId,model:row.key,app:row.app}})
}

const {crudBinding, crudRef, crudExpose} = useFs({createCrudOptions,props});
onMounted(async () => {
  const res = await getModelList();
  allModelData.value = res.data;
});



</script>

<style scoped lang="scss">
.model-card{
  height: 20vh;
  overflow-y: scroll;
  div{
    margin: 15px 0;
    cursor: pointer;
  }
}
</style>
