<template>
  <el-drawer v-model="drawerVisible" title="权限配置" direction="rtl" size="60%" :close-on-click-modal="false"
             :before-close="handleDrawerClose">
    <template #header>
      <el-row>
        <el-col :span="4">
          <div>当前角色:
            <el-tag>{{ props.roleName }}</el-tag>
          </div>
        </el-col>
      </el-row>
    </template>
   <div>
     <el-tabs type="border-card">
       <el-tab-pane label="菜单/按钮授权">
         <MenuPermission ref="menuPermissionRef" :role-id="props.roleId" @handleDrawerClose="handleDrawerClose"></MenuPermission>
       </el-tab-pane>
       <el-tab-pane label="请求接口授权"></el-tab-pane>
       <el-tab-pane label="接口权限">角色管理</el-tab-pane>
     </el-tabs>
   </div>
  </el-drawer>
</template>

<script setup lang="ts">
import {ref, onMounted, defineProps, watch, computed, reactive,nextTick} from 'vue';
import XEUtils from 'xe-utils';
import {errorNotification} from '/@/utils/message';
import {ElMessage} from 'element-plus'
import MenuPermission from "./MenuPermission/index.vue";

const props = defineProps({
  roleId: {
    type: Number,
    default: -1
  },
  roleName: {
    type: String,
    default: ''
  },
  drawerVisible: {
    type: Boolean,
    default: false
  }
})
const emit = defineEmits(['update:drawerVisible'])
const menuPermissionRef = ref()
const drawerVisible = ref(false)
watch(
    () => props.drawerVisible,
    (val) => {
      drawerVisible.value = val;
      nextTick(()=>{
        console.log(menuPermissionRef)
        menuPermissionRef.value.getMenuPremissionTreeData()
      })
      // fetchData()
    }
);
const handleDrawerClose = () => {
  emit('update:drawerVisible', false);
}


const defaultTreeProps = {
  children: 'children',
  label: 'name',
  value: 'id',
};


let collapseCurrent = ref(['1']);
let menuCurrent = ref<Partial<MenuDataType>>({});
let menuBtnCurrent = ref<number>(-1);
let dialogVisible = ref(false);
let dataPermissionRange = ref<DataPermissionRangeType[]>([]);
const formatDataRange = computed(() => {
  return function(datarange:number){
    const findItem = dataPermissionRange.value.find((i) => i.value === datarange);
    return  findItem?.label || ''
  }
})
let deptData = ref<CustomDataPermissionDeptType[]>([]);
let dataPermission = ref();
let customDataPermission = ref([]);
//获取菜单/按钮权限
const permissionTreeRef = ref();
let menuPermissionTreeData = ref<MenuDataType[]>([]);
const getMenuPremissionTreeData = async () => {
  const resMenu = await getMenuPremissionTree({role: props.roleId})
  menuPermissionTreeData.value = resMenu
  nextTick(() => {
    updateChecked(props.roleId);
  });
}

// 如果勾选节点中存在非叶子节点，tree组件会将其所有子节点全部勾选
// 所以要找出所有叶子节点，仅勾选叶子节点，tree组件会将父节点同步勾选
function getAllCheckedLeafNodeId(tree, checkedIds, temp) {
  for (let i = 0; i < tree.length; i++) {
    const item = tree[i];
    if (item.children && item.children.length !== 0) {
      getAllCheckedLeafNodeId(item.children, checkedIds, temp);
    } else {
      if (checkedIds.indexOf(item.id) !== -1) {
        temp.push(item.id);
      }
    }
  }
  return temp;
}
async function updateChecked(roleId:string|number) {
  let checkedIds = await getMenuPremissionChecked({role: roleId});
  // 找出所有的叶子节点
  checkedIds = getAllCheckedLeafNodeId(menuPermissionTreeData.value, checkedIds, []);
  permissionTreeRef.value.setCheckedKeys(checkedIds);
}

/**
 * 更新菜单权限
 */
async function updatePermission() {
  const roleId = props.roleId;
  const { checked, halfChecked } = permissionTreeRef.value.getChecked();
  const allChecked = [...checked, ...halfChecked];
  const menuIds = allChecked.filter(item=>item !== -1)
  await saveMenuPremission({role: roleId, menu: menuIds})
  handleDrawerClose();
  //await updateChecked(roleId);

  ElMessage.success("授权成功");
}

const fetchData = async () => {
  try {
    const resRange = await getDataPermissionRange();
    if (resRange?.code === 2000) {
      dataPermissionRange.value = resRange.data;
    }
  } catch {
    return;
  }
};

const handleCollapseChange = (val: string) => {
  collapseCurrent.value = [val];
};

/**
 * 设置按钮数据权限
 * @param record 当前菜单
 * @param btnType  按钮类型
 */
const handleSettingClick = (record: MenuDataType, btnId: number) => {
  menuCurrent.value = record;
  menuBtnCurrent.value = btnId;
  dialogVisible.value = true;
};

const handleColumnChange = (val: boolean, record: MenuDataType, btnType: string) => {
  for (const iterator of record.columns) {
    iterator[btnType] = val;
  }
};

const handlePermissionRangeChange = async (val: number) => {
  if (val === 4) {
    const res = await getDataPermissionDept();
    const data = XEUtils.toArrayTree(res.data, {parentKey: 'parent', strict: false});
    deptData.value = data;
  }
};

/**
 * 数据权限设置确认
 */
const handleDialogConfirm = () => {
  if (dataPermission.value !== 0 && !dataPermission.value) {
    errorNotification('请选择');
    return;
  }

  //if (dataPermission.value !== 4) {}
  for (const iterator of menuData.value) {
    if (iterator.id === menuCurrent.value.id) {
      for (const btn of iterator.btns) {
        if (btn.id === menuBtnCurrent.value) {
          const findItem = dataPermissionRange.value.find((i) => i.value === dataPermission.value);
          btn.data_range = findItem?.value || 0;
          if(btn.data_range===4){
            btn.dept = customDataPermission.value
          }
        }
      }
    }
  }
  handleDialogClose();
};
const handleDialogClose = () => {
  dialogVisible.value = false;
  customDataPermission.value = [];
  dataPermission.value = null;
};

//保存权限
const handleSavePermission = () => {
  setRolePremission(props.roleId, menuData.value).then(res => {
    ElMessage({
      message: res.msg,
      type: 'success',
    })
  })
}

const column = reactive({
  header:[{value:'is_create',label:'新增可见'},{value:'is_update',label:'编辑可见'},{value:'is_query',label:'列表可见'}]
})

onMounted(() => {
});
</script>

<style lang="scss" scoped>
.permission-com {
  margin: 15px;
  box-sizing: border-box;

  .pc-save-btn {
    margin-bottom: 15px;
  }

  .pc-collapse-title {
    line-height: 32px;

    span {
      font-size: 16px;
    }
  }

  .pc-collapse-main {
    padding-top: 15px;
    box-sizing: border-box;

    .pccm-item {
      margin-bottom: 10px;

      .btn-item {
        display: flex;
        align-items: center;

        span {
          margin-left: 5px;
        }
      }

      .columns-list {
        .width-txt {
          width: 200px;
        }

        .width-check {
          width: 100px;
        }

        .width-icon {
          cursor: pointer;
        }

        .columns-head {
          display: flex;
          align-items: center;
          padding: 6px 0;
          border-bottom: 1px solid #ebeef5;
          box-sizing: border-box;

          span {
            font-weight: 900;
          }
        }

        .columns-item {
          display: flex;
          align-items: center;
          padding: 6px 0;
          box-sizing: border-box;

          .ci-checkout {
            height: auto !important;
          }
        }
      }
    }
  }

  .pc-dialog {
    .dialog-select {
      width: 100%;
    }

    .dialog-tree {
      width: 100%;
      margin-top: 20px;
    }
  }
}
</style>

<style lang="scss">
.permission-com {
  .el-collapse {
    border-top: none;
    border-bottom: none;
  }

  .el-collapse-item {
    margin-bottom: 15px;
  }

  .el-collapse-item__header {
    height: auto;
    padding: 15px;
    border-radius: 8px;
    border-top: 1px solid #ebeef5;
    border-left: 1px solid #ebeef5;
    border-right: 1px solid #ebeef5;
    box-sizing: border-box;
  }

  .el-collapse-item__header.is-active {
    border-radius: 8px 8px 0 0;
    background-color: #fafafa;
  }

  .el-collapse-item__wrap {
    padding: 15px;
    border-left: 1px solid #ebeef5;
    border-right: 1px solid #ebeef5;
    border-top: 1px solid #ebeef5;
    border-radius: 0 0 8px 8px;
    background-color: #fafafa;
    box-sizing: border-box;

    .el-collapse-item__content {
      padding-bottom: 0;
    }
  }
}
</style>
