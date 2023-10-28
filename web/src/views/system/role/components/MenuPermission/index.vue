<template>
 <div>
   <MenuPermissionTree
       ref="permissionTreeRef"
       :tree="menuPermissionTreeData"
       :default-expand-all="true"
       :editable="false"
       node-key="id"
       show-checkbox
       :props="{ label: 'title' }"></MenuPermissionTree>
   <div style="margin-top: 2em">
     <el-button type="primary" @click="updatePermission">确定</el-button>
   </div>
 </div>
</template>

<script setup lang="ts">
import {ref, onMounted, defineProps, watch, computed, reactive,nextTick} from 'vue';
import XEUtils from 'xe-utils';
import {errorNotification} from '/@/utils/message';
import {getDataPermissionRange, getDataPermissionDept, getMenuPremissionTree, saveMenuPremission,getMenuPremissionChecked} from './api';
import {MenuDataType, DataPermissionRangeType, CustomDataPermissionDeptType} from './types';
import {ElMessage} from 'element-plus'
import MenuPermissionTree from "./menuPermissionTree.vue";

const props = defineProps({
  roleId: {
    type: Number,
    default: -1
  }
})

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
  ElMessage.success("授权成功");
}

const emit = defineEmits(['handleDrawerClose']);
const handleDrawerClose = () => {
  emit('handleDrawerClose')
}

defineExpose({getMenuPremissionTreeData})
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
