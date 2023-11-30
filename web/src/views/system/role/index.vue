<template>
	<fs-page>
		<fs-crud ref="crudRef" v-bind="crudBinding">
			<template #cell_url="scope">
				<el-tag size="small">{{ scope.row.url }}</el-tag>
			</template>
		</fs-crud>

		<permission ref="rolePermission"></permission>

		<PermissionComNew v-model:drawerVisible="drawerVisible" :roleId="roleId" :roleName="roleName" @drawerClose="handleDrawerClose" />
	</fs-page>
</template>

<script lang="ts" setup name="role">
import {ref, onMounted, inject, onBeforeUpdate} from 'vue';
import { useColumnPermission } from '/@/stores/columnPermission';
import { GetPermission } from './api';
import { useExpose, useCrud } from '@fast-crud/fast-crud';
import { createCrudOptions } from './crud';
import PermissionComNew from './components/PermissionComNew/index.vue';
import _ from "lodash-es";
import {columnPermission} from "/@/utils/columnPermission";
let drawerVisible = ref(false);
let roleId = ref(null);
let roleName = ref(null);

const rolePermission = ref();
// crud组件的ref
const crudRef = ref();
// crud 配置的ref
const crudBinding = ref();


const fetchColumnPermission = async () => {
	const res = await GetPermission();
	useColumnPermission().setPermissionData(res.data);
  console.log(3333,res)
};

const handleDrawerOpen = (row: any) => {
	roleId.value = row.id;
	roleName.value = row.name;
	drawerVisible.value = true;
};

const handleDrawerClose = () => {
	drawerVisible.value = false;
};

const { crudExpose } = useExpose({ crudRef, crudBinding });
const handlecolumnPermission = async (crudOptions:any)=>{
  const res = await GetPermission();
  const columns = crudOptions.columns;
  for(let col in columns){
    for(let i in res.data){
      if(res.data[i].field_name === col){
        columns[col].column.show = i['is_query']
        columns[col].addForm = {
          show:i['is_create']
        }
        columns[col].editForm = {
          show:i['is_update']
        }
        break;
      }
    }
  }
}

// 你的crud配置
const { crudOptions } = createCrudOptions({ crudExpose, rolePermission, handleDrawerOpen });



// 页面打开后获取列表数据
onMounted( async () => {

  await handlecolumnPermission(crudOptions)
  // //合并新的crudOptions
  // const newOptions = _.merge(crudOptions, {
  //   columns: {
  //     text: {
  //       title: "追加字段",
  //       type: "text"
  //     }
  //   }
  // });
  //重置crudBinding
  // resetCrudOptions(newOptions);
// 初始化crud配置
  const { resetCrudOptions } = useCrud({
    crudExpose,
    crudOptions,
    context: {},
  });
	crudExpose.doRefresh();
});

defineExpose(rolePermission);
</script>
