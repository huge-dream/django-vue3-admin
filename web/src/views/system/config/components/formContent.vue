<template>
  <div>
    <el-row :gutter="20">
      <el-col :span="4">变量标题</el-col>
      <el-col :span="4">变量名</el-col>
      <el-col :span="10">变量值</el-col>
      <el-col :span="2" :offset="1">是否前端配置</el-col>
      <el-col :span="3" >操作</el-col>
    </el-row>
    <el-form ref="formRef" :model="formData" label-width="0px" label-position="left" style="margin-top: 20px">
      <el-form-item
          :prop="['array'].indexOf(item.form_item_type_label) > -1 ? '' : item.key"
          :key="index"
          :rules="item.rule || []"
          v-for="(item, index) in formList"
      >
        <el-col :span="4">
          <el-input v-if="item.edit" v-model="item.title" style="display: inline-block; width: 200px" placeholder="请输入标题"></el-input>
          <span v-else>{{ item.title }}</span>
        </el-col>
        <el-col :span="4" >
          <el-input v-if="item.edit" v-model="item.new_key" style="width: 200px" placeholder="请输入变量key">
            <template slot="prepend">
              <span style="padding: 0px 5px">{{ editableTabsItem.key }}</span>
            </template>
          </el-input>
          <span v-else>{{ editableTabsItem.key }}.{{ item.key }}</span>
        </el-col>
        <el-col :span="10">
          <!--    文本      -->
          <el-input
              :key="index"
              v-if="['text', 'textarea'].indexOf(item.form_item_type_label) > -1"
              :type="item.form_item_type_label"
              v-model="formData[item.key]"
              :placeholder="item.placeholder"
              clearable
          ></el-input>

          <el-input-number :key="index + 1" v-else-if="item.form_item_type_label === 'number'" v-model="formData[item.key]" :min="0"></el-input-number>
          <!--     datetime、date、time     -->
          <el-date-picker
              v-else-if="['datetime', 'date', 'time'].indexOf(item.form_item_type_label) > -1"
              v-model="formData[item.key]"
              :key="index + 2"
              :type="item.form_item_type_label"
              :placeholder="item.placeholder"
          >
          </el-date-picker>
          <!--    select      -->
          <el-select
              :key="index + 3"
              v-else-if="item.form_item_type_label === 'select'"
              v-model="formData[item.key]"
              :placeholder="item.placeholder"
              clearable
          >
            <el-option v-for="item in dictionary(item.setting) || []" :key="item.value" :label="item.label" :value="item.value"> </el-option>
          </el-select>
          <!--    checkbox      -->
          <el-checkbox-group
              :key="index + 4"
              v-else-if="item.form_item_type_label === 'checkbox'"
              v-model="formData[item.key]"
              :placeholder="item.placeholder"
          >
            <el-checkbox v-for="item in dictionary(item.setting) || []" :key="item.value" :label="item.value" :value="item.value">
              {{ item.label }}
            </el-checkbox>
          </el-checkbox-group>
          <!--    radio      -->
          <el-radio-group
              :key="index + 5"
              v-else-if="item.form_item_type_label === 'radio'"
              v-model="formData[item.key]"
              :placeholder="item.placeholder"
              clearable
          >
            <el-radio v-for="item in dictionary(item.setting) || []" :key="item.value" :label="item.value" :value="item.value">
              {{ item.label }}
            </el-radio>
          </el-radio-group>
          <!--    switch      -->
          <el-switch
              :key="index + 6"
              v-else-if="item.form_item_type_label === 'switch'"
              v-model="formData[item.key]"
              :inactive-value="false"
              active-color="#13ce66"
              inactive-color="#ff4949"
          >
          </el-switch>
          <!--     图片     -->
          <div v-else-if="['img', 'imgs'].indexOf(item.form_item_type_label) > -1" :key="index + 7">
            <el-upload
                :action="uploadUrl"
                :headers="uploadHeaders"
                name="file"
                :accept="'image/*'"
                :on-preview="handlePictureCardPreview"
                :on-success="
								(response:any, file:any, fileList:any) => {
									handleUploadSuccess(response, file, fileList, item.key);
								}
							"
                :on-error="handleError"
                :on-exceed="handleExceed"
                :before-remove="
								(file:any, fileList:any) => {
									beforeRemove(file, fileList, item.key);
								}
							"
                :multiple="item.form_item_type_label !== 'img'"
                :limit="item.form_item_type_label === 'img' ? 1 : 5"
                :ref="'imgUpload_' + item.key"
                :data-keyname="item.key"
                :file-list="item.value ? item.value : []"
                list-type="picture-card"
            >
              <i class="el-icon-plus"></i>
              <div slot="tip" class="el-upload__tip">请选取图片,并且只能上传jpg/png文件</div>
            </el-upload>
            <el-dialog :visible.sync="dialogImgVisible">
              <img width="100%" :src="dialogImageUrl" alt="" />
            </el-dialog>
          </div>
          <!--     文件     -->
          <div v-else-if="['file'].indexOf(item.form_item_type_label) > -1" :key="index + 8">
            <el-upload
                :action="uploadUrl"
                :headers="uploadHeaders"
                name="file"
                :on-preview="handlePictureCardPreview"
                :on-success="
								(response:any, file:any, fileList:any) => {
									handleUploadSuccess(response, file, fileList, item.key);
								}
							"
                :on-error="handleError"
                :on-exceed="handleExceed"
                :before-remove="
								(file:any, fileList:any) => {
									beforeRemove(file, fileList, item.key);
								}
							"
                :limit="5"
                :ref="'fileUpload_' + item.key"
                :data-keyname="item.key"
                :file-list="item.value"
                list-type="picture-card"
            >
              <i class="el-icon-plus"></i>
              <div slot="tip" class="el-upload__tip">请选取图片,并且只能上传jpg/png文件</div>
            </el-upload>
            <el-dialog :visible.sync="dialogImgVisible">
              <img width="100%" :src="dialogImageUrl" alt="" />
            </el-dialog>
          </div>
          <!--    关联表      -->
          <div v-else-if="['foreignkey', 'manytomany'].indexOf(item.form_item_type_label) > -1" :key="index + 9">
            <table-selector
                v-model="formData[item.key]"
                :el-props="{
								pagination: true,
								columns: item.setting.searchField,
							}"
                :dict="{
								url: '/api/system/system_config/get_table_data/' + item.id + '/',
								value: item.setting.primarykey,
								label: item.setting.field,
							}"
                :pagination="true"
                :multiple="item.form_item_type_label === 'manytomany'"
            ></table-selector>
          </div>
          <!--   数组       -->
          <div v-else-if="item.form_item_type_label === 'array'" :key="index + 10">
            <vxe-table
                border
                resizable
                auto-resize
                show-overflow
                keep-source
                :ref="'xTable_' + item.key"
                height="200"
                :edit-rules="validRules"
                :edit-config="{ trigger: 'click', mode: 'row', showStatus: true }"
            >
              <vxe-column field="title" title="标题" :edit-render="{ autofocus: '.vxe-input--inner' }">
                <template #edit="{ row }">
                  <vxe-input v-model="row.title" type="text"></vxe-input>
                </template>
              </vxe-column>
              <vxe-column field="key" title="键名" :edit-render="{ autofocus: '.vxe-input--inner' }">
                <template #edit="{ row }">
                  <vxe-input v-model="row.key" type="text"></vxe-input>
                </template>
              </vxe-column>
              <vxe-column field="value" title="键值" :edit-render="{}">
                <template #edit="{ row }">
                  <vxe-input v-model="row.value" type="text"></vxe-input>
                </template>
              </vxe-column>
              <vxe-column title="操作" width="100" show-overflow>
                <template #default="{ row, index }">
                  <el-popover placement="top" width="160" v-model="childRemoveVisible">
                    <p>删除后无法恢复,确定删除吗？</p>
                    <div style="text-align: right; margin: 0">
                      <el-button size="mini" type="text" @click="childRemoveVisible = false">取消</el-button>
                      <el-button type="primary" size="mini" @click="onRemoveChild(row, index, item.key)">确定</el-button>
                    </div>
                    <el-button type="text" slot="reference">删除</el-button>
                  </el-popover>
                </template>
              </vxe-column>
            </vxe-table>
            <div>
              <el-button size="mini" @click="onAppend('xTable_' + item.key)">追加</el-button>
            </div>
          </div>
        </el-col>
        <el-col :span="2" :offset="1">
          <el-switch v-model="item.status" active-color="#13ce66" inactive-color="#ff4949"> </el-switch>
        </el-col>
        <el-col :span="3">
          <el-button v-if="item.edit" size="mini" type="primary" :icon="Finished" @click="onEditSave(item)">保存</el-button>
          <el-button v-else size="mini" type="primary" :icon="Edit" @click="onEdit(index)"></el-button>
          <el-popconfirm title="确定删除该条数据吗？" @confirm="onDelRow(item)">
            <template #reference>
              <el-button size="mini" type="danger" :icon="Delete" ></el-button>
            </template>
          </el-popconfirm>
        </el-col>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="onSubmit(formRef)">确定</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import * as api from '../api';
import { dictionary } from '/@/utils/dictionary';
import { getBaseURL } from '/@/utils/baseUrl';
import { ref, reactive, watch, nextTick,inject  } from 'vue';
import type { FormInstance, FormRules, TableInstance } from 'element-plus';
import { successMessage, errorMessage } from '/@/utils/message';
import { Session } from '/@/utils/storage';
import {Edit,Finished,Delete} from "@element-plus/icons-vue";
const props = defineProps(['options', 'editableTabsItem']);

let formData: any = reactive({});
let formList: any = ref([]);
let childTableData = ref([]);
let childRemoveVisible = ref(false);
const validRules = reactive<FormRules>({
  title: [
    {
      required: true,
      message: '必须填写',
    },
  ],
  key: [
    {
      required: true,
      message: '必须填写',
    },
  ],
  value: [
    {
      required: true,
      message: '必须填写',
    },
  ],
});
const formRef =  ref<FormInstance>()
let uploadUrl = ref(getBaseURL() + 'api/system/file/');
let uploadHeaders = ref({
  Authorization: 'JWT ' + Session.get('token'),
});
let dialogImageUrl = ref('');
let dialogImgVisible = ref(false);
let uploadImgKey = ref(null);

// 获取数据
const getInit = () => {
  api.GetList({ parent: props.options.id, limit: 999 }).then((res: any) => {
    let data = res.data;
    formList.value = data;
    const _formData: any = {};
    for (const item of data) {
      const key = item.key;
      if (item.value) {
        _formData[key] = item.value;
      } else {
        if ([5, 12, 14].indexOf(item.form_item_type) !== -1) {
          _formData[key] = [];
        } else {
          _formData[key] = item.value;
        }
      }
      if (item.form_item_type_label === 'array') {
        console.log('test');
        nextTick(() => {
          const tableName = 'xTable_' + key;
          const tabelRef = ref<TableInstance>();
          console.log(tabelRef);
          // const $table = this.$refs[tableName][0];
          // $table.loadData(item.chinldern);
        });
      }
    }
    formData = Object.assign(formData, _formData)
  });
};

// 提交数据
const onSubmit = (formEl: FormInstance | undefined) => {
  // const form = JSON.parse(JSON.stringify(form));
  const keys = Object.keys(formData);
  const values = Object.values(formData);
  for (const index in formList.value) {
    const item = formList.value[index];
    // eslint-disable-next-line camelcase
    const form_item_type_label = item.form_item_type_label;

    // eslint-disable-next-line camelcase
    if (form_item_type_label === 'array') {
      const parentId = item.id;
      const tableName = 'xTable_' + item.key;
      // const $table = this.$refs[tableName][0];
      // const { tableData } = $table.getTableData();
      // for (const child of tableData) {
      // 	if (!child.id && child.key && child.value) {
      // 		child.parent = parentId;
      // 		child.id = null;
      // 		formList.push(child);
      // 	}
      // }
      // // 必填项的判断
      // for (const arr of item.rule) {
      // 	if (arr.required && tableData.length === 0) {
      // 		errorMessage(item.title + '不能为空');
      // 		return;
      // 	}
      // }
      // item.value = tableData;
    }
    // 赋值操作
    keys.map((mapKey, mapIndex) => {
      if (mapKey === item.key) {
        if (item.form_item_type_label !== 'array') {
          item.value = values[mapIndex];
        }
        // 必填项的验证
        if (['img', 'imgs'].indexOf(item.form_item_type_label) > -1) {
          for (const arr of item.rule) {
            if (arr.required && item.value === null) {
              errorMessage(item.title + '不能为空');
              return;
            }
          }
        }
      }
    });
  }
  // formRef.value.clearValidate();
  if (!formEl) return
  formEl.validate((valid:any) => {
    if (valid) {
      api.saveContent(formList.value).then((res:any) => {
        successMessage('保存成功');
        refreshView&&refreshView();
      });
    } else {
      console.log('error submit!!');
      return false;
    }
  });
};

// 追加
const onAppend = (tableName: any) => {
  // const $table = this.$refs[tableName][0];
  // const { tableData } = $table.getTableData();
  // const tableLength = tableData.length;
  // if (tableLength === 0) {
  // 	const { row: newRow } = $table.insert();
  // 	console.log(newRow);
  // } else {
  // 	const errMap = $table.validate().catch((errMap: any) => errMap);
  // 	if (errMap) {
  // 		errorMessage('校验不通过!');
  // 	} else {
  // 		const { row: newRow } = $table.insert();
  // 		console.log(newRow);
  // 	}
  // }
};

// 子表删除
const onRemoveChild = (row: any, index: any, refName: any) => {
  console.log(row, index);
  if (row.id) {
    api.DelObj(row.id).then((res: any) => {
      // this.refreshView();
    });
  } else {
    // this.childTableData.splice(index, 1);
    // const tableName = 'xTable_' + refName;
    // const tableData = this.$refs[tableName][0].remove(row);
    // console.log(tableData);
  }
};

// 图片预览
const handlePictureCardPreview = (file: any) => {
  dialogImageUrl = file.url;
  dialogImgVisible.value = true;
};

// 判断是否为图片
// 封装一个判断图片文件后缀名的方法
const isImage = (fileName: any) => {
  if (typeof fileName !== 'string') return;
  const name = fileName.toLowerCase();
  return name.endsWith('.png') || name.endsWith('.jpeg') || name.endsWith('.jpg') || name.endsWith('.png') || name.endsWith('.bmp');
};

// 上传成功
const handleUploadSuccess = (response: any, file: any, fileList: any, imgKey: any) => {
  const that = this;
  const { code, msg } = response;
  if (code === 2000) {
    const { url } = response.data;
    const { name } = file;
    const type = isImage(name);
    if (!type) {
      errorMessage('只允许上传图片');
    } else {
      const uploadImgKey = formData[imgKey];
      if (!uploadImgKey || uploadImgKey === '') {
        formData[imgKey] = [];
      }
      // console.log(len)
      const dict = {
        name: name,
        url: getBaseURL() + url,
      };
      formData[imgKey].push(dict);
    }
  } else {
    errorMessage('上传失败,' + JSON.stringify(msg));
  }
};

// 上传失败
const handleError = () => {
  errorMessage('上传失败');
};

// 上传超出限制
const handleExceed = () => {
  errorMessage('超过文件上传数量');
};

// 删除时的钩子
const beforeRemove = (file: any, fileList: any, key: any) => {
  var index = 0;
  formData[key].map((value: any, inx: any) => {
    if (value.uid === file.uid) index = inx;
  });
  formData[key].splice(index, 1);
};

// 配置的行删除
const onDelRow = (obj: any) => {
  api.DelObj(obj.id).then((res: any) => {
    // this.refreshView();
  });
};

// 行编辑
const onEdit = (index: any) => {
  formList.value[index].edit =true
  formList.value[index].new_key =formList.value[index].key
};
// 行编辑保存
const refreshView = inject<Function>('refreshView')
const onEditSave = (obj: any) => {
  obj.key = JSON.parse(JSON.stringify(obj.new_key));
  api.UpdateObj(obj).then((res: any) => {
    refreshView && refreshView()
  });
};

watch(
    props.options,
    (nv) => {
      if (nv && nv.id) {
        getInit();
      }
    },
    { immediate: true }
);
</script>

<style scoped>
:deep(.el-upload-list--picture-card){
  text-align: center;
}
</style>
