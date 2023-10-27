<template>
  <fs-page>
    <fs-crud ref="crudRef" v-bind="crudBinding">

    </fs-crud>
    <fs-form-wrapper ref="addChildrenRef" />
  </fs-page>
</template>

<script lang="ts" setup>
import {ref, onMounted, reactive, computed} from "vue";
import createCrudOptions from "./crud";
import {useExpose, useCrud, useCompute} from "@fast-crud/fast-crud";
import {AddObj} from "./api";
import {ElMessage } from "element-plus"



// crud组件的ref
const crudRef = ref();
// crud 配置的ref
const crudBinding = ref();
// 暴露的方法
const { crudExpose } = useExpose({ crudRef, crudBinding });



// 添加目录
const onAddCatalog = (row:any)=>{
  const childrenOptions = ref();
  childrenOptions.value = {...crudBinding.value.addForm};
  childrenOptions.value.columns.parent_name.show = false
  childrenOptions.value.columns.icon.show = true
  childrenOptions.value.columns.web_path.show = false
  childrenOptions.value.columns.is_link.show = false
  childrenOptions.value.columns.cache.show = false
  childrenOptions.value.columns.web_path.show = false
  childrenOptions.value.columns.visible.show = false
  childrenOptions.value.columns.frame_out.show = false
  childrenOptions.value.columns.sort.show = true
  childrenOptions.value.columns.status.show = true
  childrenOptions.value.columns.component.show = false
  childrenOptions.value.initialForm = { menu_type:0,web_path:'/' };
  //覆盖提交方法
  childrenOptions.value.doSubmit=({ form })=>{
   AddObj(form).then(res=>{
     ElMessage.success('添加成功')
     childrenOptions.value.onSuccess()
     addChildrenRef.value.close()
   })
  }
  addChildrenRef.value.open(childrenOptions.value);
}

// 添加子级
const addChildrenRef = ref();
const onAddChildren = (row:any)=>{
  const childrenOptions = ref();
  childrenOptions.value = {...crudBinding.value.addForm};
  childrenOptions.value.columns.parent_name.show = true
  childrenOptions.value.columns.is_link.show = true
  childrenOptions.value.columns.cache.show = true
  childrenOptions.value.columns.web_path.show = true
  childrenOptions.value.columns.component.show = true
  childrenOptions.value.columns.component.title = "组件地址"
  childrenOptions.value.columns.visible.show = true
  childrenOptions.value.columns.frame_out.show = true
  childrenOptions.value.columns.status.show = true
  childrenOptions.value.initialForm = { parent_name: row.name,menu_type:1 };
  //覆盖提交方法
  childrenOptions.value.doSubmit=({ form })=>{
    form.parent = row.id
    AddObj(form).then(res=>{
      ElMessage.success('添加成功')
      childrenOptions.value.onSuccess()
      addChildrenRef.value.close()
    })
  }
  addChildrenRef.value.open(childrenOptions.value);
}

// 添加按钮
const onAddButton = (row:any)=>{
  const childrenOptions = ref();
  childrenOptions.value = {...crudBinding.value.addForm};
  childrenOptions.value.columns.parent_name.show = true
  childrenOptions.value.columns.icon.show = false
  childrenOptions.value.columns.web_path.show = false
  childrenOptions.value.columns.is_link.show = false
  childrenOptions.value.columns.cache.show = false
  childrenOptions.value.columns.web_path.show = false
  childrenOptions.value.columns.visible.show = false
  childrenOptions.value.columns.frame_out.show = false
  childrenOptions.value.columns.sort.show = false
  childrenOptions.value.columns.status.show = false
  childrenOptions.value.columns.component.show = true
  childrenOptions.value.columns.component.title = "按钮权限值"
  childrenOptions.value.initialForm = { parent_name: row.name,menu_type:2 };
  //覆盖提交方法
  childrenOptions.value.doSubmit=({ form })=>{
    form.parent = row.id
    AddObj(form).then(res=>{
      ElMessage.success('添加成功')
      childrenOptions.value.onSuccess()
      addChildrenRef.value.close()
    })
  }
  addChildrenRef.value.open(childrenOptions.value);
}


// 你的crud配置
const { crudOptions } = createCrudOptions({ crudExpose,onAddCatalog,onAddChildren,onAddButton });
// 初始化crud配置
// eslint-disable-next-line @typescript-eslint/no-unused-vars,no-unused-vars
const { resetCrudOptions } = useCrud({ crudExpose, crudOptions });
// 你可以调用此方法，重新初始化crud配置
// resetCrudOptions(options)

// 页面打开后获取列表数据
onMounted(() => {
  crudExpose.doRefresh();
});
</script>
