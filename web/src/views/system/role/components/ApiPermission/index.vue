<template>
  <div style="height: 86vh">
    <fs-crud ref="crudRef" v-bind="crudBinding">
      <template #form_dept="scope">
        <div>
          <el-tree-select
              v-model="scope.form.dept"
              :data="allDeptData"
              :props="treeProps"
              node-key="id"
              multiple
              :render-after-expand="false"
              show-checkbox
              check-strictly
              check-on-click-node
          >
            <template #default="{ data: { name } }">
              {{ name }}
            </template
            >
          </el-tree-select>
        </div>
      </template>
    </fs-crud>
  </div>
</template>

<script lang="ts" setup>
import {ref, onMounted, reactive} from 'vue';
import {useFs} from '@fast-crud/fast-crud';
import {createCrudOptions} from './crud';
import {GetAllDeptData} from './api'
const propsContext = defineProps({
  roleId:{
    type:String||Number,
    required:true
  }
})
const {crudBinding, crudRef, crudExpose} = useFs({createCrudOptions,propsContext});

// 获取所有部门数据
const allDeptData = ref<any[]>([]);
const treeProps ={
  label: 'name',
  value: 'id',
  children: 'children',
}

onMounted(async () => {
  const res = await GetAllDeptData({role:propsContext.roleId});
  allDeptData.value = res;
  crudExpose.doSearch({form:{role:propsContext.roleId}})
});

</script>

<style scoped>

</style>
