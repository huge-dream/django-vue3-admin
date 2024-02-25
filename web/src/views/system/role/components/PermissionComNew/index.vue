<template>
  <el-drawer v-model="drawerVisible" title="权限配置" direction="rtl" size="60%" :close-on-click-modal="false"
             :before-close="handleDrawerClose"
             :destroy-on-close="true"
  >
    <template #header>
      <el-row>
        <el-col :span="4">
          <div>当前授权角色:
            <el-tag>{{ props.roleName }}</el-tag>
          </div>
        </el-col>
        <el-col :span="6">
          <div>
            <el-button size="small" type="primary" class="pc-save-btn" @click="handleSavePermission">保存菜单授权
            </el-button>
          </div>
        </el-col>
      </el-row>
    </template>
    <div class="permission-com">
      <el-collapse v-model="collapseCurrent" @change="handleCollapseChange" accordion>
        <el-collapse-item v-for="(item,mIndex) in menuData" :key="mIndex" :name="mIndex"
                          style="    background-color: #fafafa;">
          <template #title>
            <div>
              <div class="pc-collapse-title">
                <el-checkbox v-model="item.isCheck" @click.stop="null">
                  <span>{{ item.name }}</span>
                </el-checkbox>
              </div>
              <div v-show="!collapseCurrent.includes(mIndex)" @click.stop="null" style="text-align: left;">
                <el-checkbox v-for="btn in item.btns" :key="btn.value" :label="btn.value" v-model="btn.isCheck">
                  {{ btn.name }}
                </el-checkbox>
              </div>
            </div>
          </template>
          <div class="pc-collapse-main">
            <div class="pccm-item">
              <p>允许对这些数据有以下操作</p>
              <el-checkbox v-for="(btn,bIndex) in item.btns" :key="bIndex" v-model="btn.isCheck" :label="btn.value">
                <div class="btn-item">
                  {{ btn.data_range !== null ? `${btn.name}(${formatDataRange(btn.data_range)})` : btn.name }}
                  <span v-show="btn.isCheck" @click.stop.prevent="handleSettingClick(item, btn.id)">
                    <el-icon><Setting/></el-icon>
                  </span>
                </div>
              </el-checkbox>
            </div>

            <div class="pccm-item" v-if="item.columns&&item.columns.length>0">
              <p>对这些数据有以下字段权限</p>

              <ul class="columns-list">
                <li class="columns-head">
                  <div class="width-txt">
                    <span>字段</span>
                  </div>

                  <div v-for="(head,hIndex) in column.header" :key="hIndex" class="width-check">
                    <el-checkbox :label="head.value" @change="handleColumnChange($event, item, head.value)">
                      <span>{{ head.label }}</span>
                    </el-checkbox>
                  </div>
                </li>

                <li v-for="(c_item, c_index) in item.columns" :key="c_index" class="columns-item">
                  <div class="width-txt">{{ c_item.title }}</div>
                  <div v-for="(col,cIndex) in column.header" :key="cIndex" class="width-check">
                    <el-checkbox v-model="c_item[col.value]" class="ci-checkout"></el-checkbox>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </el-collapse-item>
      </el-collapse>

      <el-dialog v-model="dialogVisible" title="数据权限配置" width="400px" :close-on-click-modal="false"
                 :before-close="handleDialogClose">
        <div class="pc-dialog">
          <el-select v-model="dataPermission" @change="handlePermissionRangeChange" class="dialog-select"
                     placeholder="请选择">
            <el-option v-for="item in dataPermissionRange" :key="item.value" :label="item.label" :value="item.value"/>
          </el-select>
          <el-tree-select
              v-show="dataPermission === 4"
              node-key="id"
              v-model="customDataPermission"
              :props="defaultTreeProps"
              :data="deptData"
              multiple
              check-strictly
              :render-after-expand="false"
              show-checkbox
              class="dialog-tree"
          />
        </div>
        <template #footer>
          <div>
            <el-button type="primary" @click="handleDialogConfirm"> 确定</el-button>
            <el-button @click="handleDialogClose"> 取消</el-button>
          </div>
        </template>
      </el-dialog>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import {ref, onMounted, defineProps, watch, computed, reactive} from 'vue';
import XEUtils from 'xe-utils';
import {errorNotification} from '/@/utils/message';
import {
  getDataPermissionRange,
  getDataPermissionDept,
  getRolePremission,
  setRolePremission,
  setBtnDatarange
} from './api';
import {MenuDataType, DataPermissionRangeType, CustomDataPermissionDeptType} from './types';
import {ElMessage} from 'element-plus'

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

const drawerVisible = ref(false)
watch(
    () => props.drawerVisible,
    (val) => {
      drawerVisible.value = val;
      getMenuBtnPermission()
      fetchData()
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

let menuData = ref<MenuDataType[]>([]);
let collapseCurrent = ref(['1']);
let menuCurrent = ref<Partial<MenuDataType>>({});
let menuBtnCurrent = ref<number>(-1);
let dialogVisible = ref(false);
let dataPermissionRange = ref<DataPermissionRangeType[]>([]);
const formatDataRange = computed(() => {
  return function (datarange: number) {
    const findItem = dataPermissionRange.value.find((i) => i.value === datarange);
    return findItem?.label || ''
  }
})
let deptData = ref<CustomDataPermissionDeptType[]>([]);
let dataPermission = ref();
let customDataPermission = ref([]);
//获取菜单,按钮,权限
const getMenuBtnPermission = async () => {
  const resMenu = await getRolePremission({role: props.roleId})
  menuData.value = resMenu.data
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
          if (btn.data_range === 4) {
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
  header: [{value: 'is_create', label: '新增可见'}, {value: 'is_update', label: '编辑可见'}, {
    value: 'is_query',
    label: '列表可见'
  }]
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
    text-align: left;

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
    background-color: #fafafa;
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
