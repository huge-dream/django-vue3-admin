<template>
  <el-select
      popper-class="right-side-dropdown"
      class="tableSelector"
      multiple
      @remove-tag="removeTag"
      v-model="data"
      placeholder="请选择"
      @visible-change="visibleChange"
      clearable
      placement="right-start"
      popper-append-to-body
  >
    <template #empty>
      <div class="option" style="width: 700px">
        <el-row :gutter="24">
          <el-col :span="12" v-for="(item, index) in props.tableConfig.search" :key="index">
            <el-row style="margin-bottom: 10px">
              <el-col :span="10">
                <span>{{ item.label }}：</span>
              </el-col>
              <el-col :span="14">
                <!-- 如果type不是daterange，则使用el-input -->
                <el-input
                    v-if="item.type !== 'daterange'"
                    :key="index"
                    v-model="search_input[item.prop]"
                    :clearable="true"
                    :placeholder="item.placeholder"
                    :type="item.type"
                    :width="item.width"
                    @change="getDict"
                    @clear="getDict"
                >
                  <template #append>
                    <el-button type="primary" icon="Search"/>
                  </template>
                </el-input>
                <!-- 如果type是daterange，则使用el-date-picker -->
                <el-date-picker
                    v-else
                    v-model="search_input[item.prop]"
                    type="daterange"
                    range-separator="To"
                    start-placeholder="起始日期"
                    end-placeholder="结束日期"
                    clearable
                    @change="getDict"
                    @clear="getDict"
                    :shortcuts="shortcuts"
                    :size="props.size"
                    value-format="YYYY-MM-DD"
                >
                  <template #append>
                    <el-button type="primary" icon="Search"/>
                  </template>
                </el-date-picker>
              </el-col>
            </el-row>
          </el-col>
        </el-row>

        <el-table
            ref="tableRef"
            :data="tableData"
            size="small"
            row-key="id"
            :lazy="props.tableConfig.lazy"
            :load="props.tableConfig.load"
            :tree-props="props.tableConfig.treeProps"
            height="300"
            :highlight-current-row="!props.tableConfig.isMultiple"
            @selection-change="handleSelectionChange"
            @current-change="handleCurrentChange"
        >
          <el-table-column v-if="props.tableConfig.isMultiple" fixed type="selection" width="50"/>
          <el-table-column
              :prop="item.prop"
              :label="item.label"
              :width="item.width"
              v-for="(item, index) in props.tableConfig.columns"
              :key="index"
          />
        </el-table>
        <el-pagination
            style="margin-top: 10px"
            background
            v-model:current-page="pageConfig.page"
            v-model:page-size="pageConfig.limit"
            layout="prev, pager, next"
            :total="pageConfig.total"
            @current-change="handlePageChange"
        />
      </div>
    </template>
  </el-select>
</template>

<script setup lang="ts">
import {defineProps, reactive, ref, watch} from 'vue';
import XEUtils from 'xe-utils';
import {request} from '/@/utils/service';

const shortcuts = [
  {
    text: '未来一周',
    value: () => {
      const end = new Date()
      const start = new Date()
      end.setTime(end.getTime() + 3600 * 1000 * 24 * 7)
      return [start, end]
    },
  },
  {
    text: '未来一个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      end.setTime(end.getTime() + 3600 * 1000 * 24 * 30)
      return [start, end]
    },
  },
  {
    text: '未来三个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      end.setTime(end.getTime() + 3600 * 1000 * 24 * 90)
      return [start, end]
    },
  },
  {
    text: '未来半年',
    value: () => {
      const end = new Date()
      const start = new Date()
      end.setTime(end.getTime() + 3600 * 1000 * 24 * 180)
      return [start, end]
    },
  },
  {
    text: '未来一年',
    value: () => {
      const end = new Date()
      const start = new Date()
      end.setTime(end.getTime() + 3600 * 1000 * 24 * 365)
      return [start, end]
    },
  },
]

interface TableConfigItem {
  prop: string;
  label?: string;
  type?: string;
  placeholder?: string;
  width?: string;
}

const props = defineProps<{
  modelValue: any;
  tableConfig: {
    url: string | null;
    label: string; // 显示值
    value: string; // 数据值
    isTree: boolean;
    lazy: boolean;
    load: () => void;
    data: any[]; // 默认数据
    isMultiple: boolean; // 是否多选
    treeProps: { children: string; hasChildren: string };
    columns: any[]; // 每一项对应的列表项
    params: Record<string, any>;
    search: TableConfigItem[]; // 搜索配置
  };
  size: string;
  displayLabel: any;
}>();

const emit = defineEmits(['update:modelValue']);
// tableRef
const tableRef = ref();
// template上使用data
const data = ref();
// 多选值
const multipleSelection = ref();
// 搜索值
const search_input = reactive<{ [key: string]: any }>({});
//表格数据
const tableData = ref();
// 分页的配置
const pageConfig = reactive({
  page: 1,
  limit: 10,
  total: 0,
});
const selectedItems = ref<Array<any>>([]);


/**
 * 表格多选
 * @param val
 */
const handleSelectionChange = (val: any) => {
  const {tableConfig} = props;

  // 更新当前页的多选项
  multipleSelection.value = val;

  // 计算并更新全局的选中集合
  val.forEach((item: any) => {
    if (!selectedItems.value.some((selected: any) => selected[tableConfig.value] === item[tableConfig.value])) {
      selectedItems.value.push(item);
    }
  });

  // 移除取消选中的项
  selectedItems.value = selectedItems.value.filter((item: any) =>
      val.some((selected: any) => selected[tableConfig.value] === item[tableConfig.value]) ||
      !tableData.value.some((dataItem: any) => dataItem[tableConfig.value] === item[tableConfig.value])
  );

  // 更新表单绑定的选中数据
  emitSelectedItems();
};

/**
 * 发射已选中项数据
 */
const emitSelectedItems = () => {
  const {tableConfig} = props;
  const result = selectedItems.value.map((item: any) => item[tableConfig.value]);
  data.value = selectedItems.value.map((item: any) => item[tableConfig.label]);
  emit('update:modelValue', result);
};
/**
 * 表格单选
 * @param val
 */
const handleCurrentChange = (val: any) => {
  const {tableConfig} = props;
  if (!tableConfig.isMultiple && val) {
    data.value = [val[tableConfig.label]];
    emit('update:modelValue', val[tableConfig.value]);
  }
};

/**
 * 获取字典值
 */
const getDict = async () => {
  const url = props.tableConfig.url;
  const params = {
    page: pageConfig.page,
    limit: pageConfig.limit,
    ...search_input,
    ...props.tableConfig.params,
  };
  const response = await request({
    url: url,
    params: params,
  });

  const {data, page, limit, total} = response;
  pageConfig.page = page;
  pageConfig.limit = limit;
  pageConfig.total = total;

  if (!props.tableConfig.data || props.tableConfig.data.length === 0) {
    if (props.tableConfig.isTree) {
      tableData.value = XEUtils.toArrayTree(data, {parentKey: 'parent', key: 'id', children: 'children'});
    } else {
      tableData.value = data;
    }
  } else {
    tableData.value = props.tableConfig.data;
  }

  // 在加载数据之后恢复选中状态
  setTableSelection();
};

/**
 * 下拉框展开/关闭
 * @param bool
 */
const visibleChange = (bool: any) => {
  if (bool) {
    getDict();
  }
};

/**
 * 分页
 * @param page
 */
const handlePageChange = (page: any) => {
  pageConfig.page = page;
  getDict().then(() => {
    // 分页数据加载后，重新设置表格的选中状态
    setTableSelection();
  });
};
/**
 * 设置表格选中项
 */
const setTableSelection = () => {
  const {tableConfig} = props;

  if (tableRef.value) {
    // 遍历表格数据，重新选中在 selectedItems 中存在的项
    tableData.value.forEach((item: any) => {
      if (selectedItems.value.some((selected: any) => selected[tableConfig.value] === item[tableConfig.value])) {
        tableRef.value.toggleRowSelection(item, true);
      }
    });
  }
};

/**
 * 移除tag
 * @param tag
 */
const removeTag = (tag: any) => {
  const {tableConfig} = props;

  // 从全局选中集合中移除对应项
  selectedItems.value = selectedItems.value.filter((item: any) => item[tableConfig.label] !== tag);

  // 更新绑定的数据
  emitSelectedItems();

  // 更新当前页的表格选中状态
  setTableSelection();
};
// 监听displayLabel的变化，更新数据
watch(
    () => {
      return props.displayLabel;
    },
    (value) => {
      const {tableConfig} = props;
      data.value = value
          ? value.map((item: any) => {
            return item[tableConfig.label];
          })
          : null;
    },
    {immediate: true}
);
</script>

<style scoped>
.option {
  height: auto;
  line-height: 1;
  padding: 5px;
  background-color: #fff;
}
</style>
<style lang="scss">
.popperClass {
  height: 320px;
}

.right-side-dropdown {
  transform-origin: right center !important; // 设置弹出框的动画起点位置
}

.el-select-dropdown__wrap {
  max-height: 310px !important;
}

.tableSelector {
  .el-icon,
  .el-tag__close {
    display: none;
  }

  .el-table__header {
    vertical-align: middle;
  }
}

</style>
