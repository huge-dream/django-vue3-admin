<template>
  <div style="display: inline-block">
    <el-button  type="success" @click="handleImport()">
      <slot>导入</slot>
    </el-button>
    <el-dialog :title="props.upload.title" v-model="uploadShow" width="400px" append-to-body>
      <div v-loading="loading">
        <el-upload
            ref="uploadRef"
            :limit="1"
            accept=".xlsx, .xls"
            :headers="props.upload.headers"
            :action="props.upload.url"
            :disabled="isUploading"
            :on-progress="handleFileUploadProgress"
            :on-success="handleFileSuccess"
            :auto-upload="false"
            drag
        >
          <i class="el-icon-upload"/>
          <div class="el-upload__text">
            将文件拖到此处，或
            <em>点击上传</em>
          </div>
          <template #tip>
          <div  class="el-upload__tip" style="color:red">提示：仅允许导入“xls”或“xlsx”格式文件！</div>
          </template>
        </el-upload>
        <div>
          <el-button type="warning" style="font-size:14px;margin-top: 20px" @click="importTemplate">下载导入模板</el-button>
          <el-button type="warning" style="font-size:14px;margin-top: 20px" @click="updateTemplate">批量更新模板</el-button>
        </div>
      </div>
      <template #footer>
      <div  class="dialog-footer">
        <el-button type="primary" :disabled="loading" @click="submitFileForm">确 定</el-button>
        <el-button :disabled="loading" @click="uploadShow = false">取 消</el-button>
      </div>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup name="importExcel">
import { request, downloadFile } from '/@/utils/service';
import {inject,ref} from "vue";
import { getBaseURL } from '/@/utils/baseUrl';
import { Session } from '/@/utils/storage';
import {  ElMessageBox } from 'element-plus'
import type { Action } from 'element-plus'
const refreshView = inject('refreshView')

let props = defineProps({
  upload: {
    type: Object,
    default () {
      return {
        // 是否显示弹出层
        open: true,
        // 弹出层标题
        title: '',
        // 是否禁用上传
        isUploading: false,
        // 是否更新已经存在的用户数据
        updateSupport: 0,
        // 设置上传的请求头部
        headers: { Authorization: 'JWT ' + Session.get('token') },
        // 上传的地址
        url: getBaseURL() + 'api/system/file/'
      }
    }
  },
  api: { // 导入接口地址
    type: String,
    default () {
      return undefined
    }
  }
})

let loading = ref(false)
const uploadRef = ref()
const uploadShow = ref(false)
const isUploading = ref(false)
/** 导入按钮操作 */
const handleImport = function () {
  uploadShow.value = true
}

/** 下载模板操作 */
const importTemplate=function () {
  downloadFile({
    url: props.api + 'import_data/',
    params: {},
    method: 'get'
  })
}
/***
 * 批量更新模板
 */
const updateTemplate=function () {
  downloadFile({
    url: props.api + 'update_template/',
    params: {},
    method: 'get'
  })
}
// 文件上传中处理
const handleFileUploadProgress=function (event:any, file:any, fileList:any) {
  isUploading.value = true
}
// 文件上传成功处理
const handleFileSuccess=function (response:any, file:any, fileList:any) {
  isUploading.value = false
  loading.value = true
  uploadRef.value.clearFiles()
  // 是否更新已经存在的用户数据
  return request({
    url: props.api + 'import_data/',
    method: 'post',
    data: {
      url: response.data.url
    }
  }).then((response:any) => {
    loading.value = false
    ElMessageBox.alert('导入成功', '导入完成', {
      confirmButtonText: 'OK',
      callback: (action: Action) => {
        refreshView()
      },
    })
  }).catch(()=>{
    loading.value = false
  })

}
// 提交上传文件
const submitFileForm=function () {
  uploadRef.value.submit()
}

</script>

<style scoped>

</style>
