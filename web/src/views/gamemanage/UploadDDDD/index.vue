<template>
  <div>
    <el-container>
      <el-main>
        <el-upload
            class="upload"
            drag
            accept=".xls,.xlsx,.csv"
            :http-request="handleFileRead"
            :before-remove="beforeRemove"
            :on-remove="handleRemove"
            :show-file-list="true"
            :limit="1"
        >
          <el-icon class="el-icon--upload">
            <upload-filled/>
          </el-icon>
          <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
          <div class="el-upload__tip" slot="tip">每次只能上传一个文件, 上传前请确保文件名以四位年份信息开头</div>
          <div class="el-upload__tip" slot="tip">需要先设置时间范围，再上传文件</div>
          <template #tip>
            <div class="el-upload__tip">仅支持 .xls, .xlsx, .csv 文件</div>
          </template>
        </el-upload>
        <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            :default-time="defaultTimeRange"
            class="date-picker"
        />
        <el-button
            type="primary"
            @click="uploadToServer"
            class="upload-button"
        >
          上传
        </el-button>
        <div v-if="sheetData.length" ref="tabsWrapper">
          <el-tabs
              v-model="activeTab"
              ref="tabs"
              :scrollable="true"
          >
            <el-tab-pane
                v-for="(sheet, sheetIndex) in filteredSheetData"
                :key="sheetIndex"
                :label="sheet.sheetName"
                :name="String(sheetIndex)"
            >
              <el-descriptions direction="vertical" :column="4" border v-if="!sheet.scheduling">
                <el-descriptions-item label="表格" width="10%">游戏信息</el-descriptions-item>
                <el-descriptions-item label="游戏名" width="50%">{{ sheet.gameName }}</el-descriptions-item>
                <el-descriptions-item label="上线日期" width="20%">{{ sheet.releaseDate }}</el-descriptions-item>
                <el-descriptions-item label="主体" width="20%">{{ sheet.parent || '靖堂（默认）' }}</el-descriptions-item>
              </el-descriptions>
              <el-descriptions direction="vertical" :column="4" border v-if="sheet.scheduling">
                <el-descriptions-item label="表格" width="10%">排期表</el-descriptions-item>
                <el-descriptions-item label="表格名" width="90%">{{ sheet.sheetName }}</el-descriptions-item>
              </el-descriptions>
              <el-table :data="sheet.tableData" style="width: 100%" border>
                <el-table-column
                    v-for="(header, headerIndex) in sheet.sheetHeaders"
                    :key="headerIndex"
                    :prop="header.prop"
                    :label="header.label"
                    show-overflow-tooltip
                />
              </el-table>
            </el-tab-pane>
          </el-tabs>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<style scoped>

.upload-button {
  margin: 10px; /* 调整外边距 */
}

.date-picker {
  margin: 10px; /* 调整外边距 */
}
</style>


<script lang="ts">
import {defineComponent, ref, computed} from 'vue';
import {UploadDDDD} from './crud';
import * as XLSX from 'xlsx';
import {
  ElContainer,
  ElHeader,
  ElMain,
  ElUpload,
  ElTabs,
  ElTabPane,
  ElButton,
  ElDatePicker,
  ElMessage, UploadProps, ElMessageBox
} from 'element-plus';
import {UploadFilled} from "@element-plus/icons-vue";

export default defineComponent({
  name: 'FileUploader',
  components: {
    UploadFilled,
    ElContainer,
    ElHeader,
    ElMain,
    ElUpload,
    ElTabs,
    ElTabPane,
    ElButton,
    ElDatePicker
  },
  setup() {
    const sheetData = ref<any[]>([]);
    const activeTab = ref('0');
    const fileData = ref<any>(null);
    const schedulingData = ref<any>(null);
    const tabsWrapper = ref<HTMLElement | null>(null);
    const unloadedSheetData = ref<string[]>([]);

    // 日期区间
    const dateRange = ref<[Date, Date]>([
      new Date(new Date().getFullYear(), new Date().getMonth() - 1, 1),
      new Date(new Date().getFullYear(), new Date().getMonth(), 15)
    ]);
    // 默认时间范围
    const defaultTimeRange: [Date, Date] = [
      new Date(new Date().getFullYear(), new Date().getMonth() - 1, 1),
      new Date(new Date().getFullYear(), new Date().getMonth(), 15)
    ];
    // 过滤后的表格数据
    const filteredSheetData = computed(() => {
      sheetData.value.forEach(sheet => {
        if (sheet.scheduling) return;
        const releaseDate = new Date(sheet.releaseDate);
        if (releaseDate < dateRange.value[0] || releaseDate > dateRange.value[1]) {
          sheetData.value = sheetData.value.filter(s => s !== sheet);
        }
      });
      return sheetData.value.filter(sheet => {
        if (sheet.scheduling) return true;
        const releaseDate = new Date(sheet.releaseDate);
        return releaseDate >= dateRange.value[0] && releaseDate <= dateRange.value[1];
      });
    });

    const beforeRemove: UploadProps['beforeRemove'] = async (uploadFile, uploadFiles) => {
      return ElMessageBox.confirm(
          `取消上传 ${uploadFile.name} ?`,
          '提示',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
      ).then(
          () => {
            return true;
          }
      ).catch(
          () => {
            return false;
          }
      );
    };

    const handleRemove: UploadProps['onRemove'] = (uploadFile) => {
      sheetData.value = [];
      fileData.value = null;
      schedulingData.value = null;
      unloadedSheetData.value = [];
      tabsWrapper.value?.scrollTo(0, 0);
      activeTab.value = '0';
      const uploadInput = document.querySelector('.el-upload__input');
      if (uploadInput) {
        (uploadInput as HTMLInputElement).value = '';
      }
    }

    const handleFileRead = async ({file}: { file: File }) => {
      const fileName = file.name;
      const matchResult = fileName.match(/\d{4}/);
      let Year: number = new Date().getFullYear();
      if (matchResult) {
        ElMessage({
          message: `匹配到的年份: ${matchResult[0]}`,
          type: 'success',
          duration: 5000
        });
        Year = Number(matchResult[0]);
      } else {
        ElMessage({
          message: '未匹配到年份, 将使用当前年份, 请检查文件名是否包含年份信息',
          type: 'warning',
          duration: 5000
        });
      }
      const reader = new FileReader();
      reader.onload = async (e) => {
        const data = new Uint8Array(e.target?.result as ArrayBuffer);
        const workbook = XLSX.read(data, {type: 'array', raw: true});
        const unloadedSheets: string[] = [];

        const validSheetNames = workbook.SheetNames.filter(sheetName => {
          const originalSheetName = sheetName.replace(' ', '');
          if (originalSheetName.includes('排期表')) { // 如果是排期表
            return true;
          }
          if (originalSheetName.includes('（') && originalSheetName.includes('）')) {
            const matchResult = originalSheetName.match(/([\u4e00-\u9fa5a-zA-Z0-9]+（[\u4e00-\u9fa5a-zA-Z0-9.]+）)(\d+\.\d+)([\u4e00-\u9fa5a-zA-Z0-9.]*)/);
            if (matchResult) {
            } else {
              unloadedSheets.push(originalSheetName);
              return false;
            }
          } else {
            const matchResult = originalSheetName.match(/[\u4e00-\u9fa5a-zA-Z0-9.]+?\d+\.\d+/);
            if (matchResult) {
            } else {
              unloadedSheets.push(originalSheetName);
              return false;
            }
          }
          return true;
        });
        if (validSheetNames.length === 0) {
          ElMessage({
            message: '未找到有效的表格',
            type: 'error',
            duration: 5000
          });
          return;
        }

        let schedulingDataIn = {};
        const sheets = validSheetNames.map(sheetName => {
          const originalSheetName = sheetName;
          const cleanSheetName = sheetName.replace(' ', '');
          const scheduling = (cleanSheetName.includes('排期表'));

          let gameName = '';
          let releaseDate = '';
          let parent = '';

          if (scheduling) {  // 如果是排期表
            const worksheet = workbook.Sheets[sheetName];
            const jsonData = XLSX.utils.sheet_to_json(worksheet, {header: 1}) as any[][]; // 读取数据，转为json格式

            const filteredData = jsonData.filter((row: any[]) => {
              return row.some(cell => cell !== null && cell !== undefined && cell !== '');  // 过滤掉空行
            });

            const stopReadingIndex = filteredData.findIndex(row => row.some(cell => cell === '停止读取')); // 找到停止读取的行
            if (stopReadingIndex !== -1) {
              filteredData.splice(stopReadingIndex);
            }

            for (let i = 0; i < filteredData.length; i++) { // 将null或undefined转为空字符串
              for (let j = 0; j < filteredData[i].length; j++) {
                if (filteredData[i][j] === null || filteredData[i][j] === undefined) {
                  filteredData[i][j] = '';
                }
              }
            }

            const onlineScheduleIndex = filteredData[0].indexOf('上线排期');  // 找到上线排期列
            if (onlineScheduleIndex !== -1) {
              for (let i = 1; i < filteredData.length; i++) {
                const cell = filteredData[i][onlineScheduleIndex];  // 检查上线排期列是否为数字
                if (cell == '' || isNaN(Number(cell))) {
                  filteredData.splice(i, 1);  // 不是数字则删除该行
                  i--;
                }
              }
            } else {
              ElMessage({
                message: '未找到上线排期列',
                type: 'error',
                duration: 5000
              });
              return null;
            }

            for (let i = 0; i < filteredData[0].length; i++) {  // 删除全为空的列
              if (filteredData.every(row => row[i] === '')) {
                filteredData.forEach(row => row.splice(i, 1));
                i--;
              }
            }

            const encodedData = filteredData.map(row =>
                row.map(cell => typeof cell === 'string' ?
                    new TextDecoder('utf-8').decode(new TextEncoder().encode(cell)) : cell)  // 编码数据
            );


            schedulingDataIn = {
              sheetName: sheetName,
              sheetHeaders: encodedData[0].map(header => ({prop: header, label: header})),
              sheetData: encodedData.slice(1),
              scheduling: scheduling
            };
          } else {
            if (cleanSheetName.includes('（') && cleanSheetName.includes('）')) {
              const matchResult = cleanSheetName.match(/([\u4e00-\u9fa5a-zA-Z0-9]+（[\u4e00-\u9fa5a-zA-Z0-9.]+）)(\d+\.\d+)([\u4e00-\u9fa5a-zA-Z0-9.]*)/);
              if (matchResult) {
                [gameName, releaseDate, parent] = matchResult.slice(1);
                const [month, day] = releaseDate.split('.').map(Number);
                const monthStr = month < 10 ? `0${month}` : `${month}`;
                const dayStr = day < 10 ? `0${day}` : `${day}`;
                releaseDate = `${Year}-${monthStr}-${dayStr}`;
              } else {
                unloadedSheets.push(originalSheetName);
                return null;
              }
            } else {
              const matchResult = cleanSheetName.match(/([\u4e00-\u9fa5a-zA-Z0-9.]+?)(\d+\.\d+)([\u4e00-\u9fa5a-zA-Z0-9.]*)/);
              if (matchResult) {
                [gameName, releaseDate, parent] = matchResult.slice(1);
                const [month, day] = releaseDate.split('.').map(Number);
                const monthStr = month < 10 ? `0${month}` : `${month}`;
                const dayStr = day < 10 ? `0${day}` : `${day}`;
                releaseDate = `${Year}-${monthStr}-${dayStr}`;
              } else {
                unloadedSheets.push(originalSheetName);
                return null;
              }
            }
          }

          const worksheet = workbook.Sheets[sheetName];
          const jsonData = XLSX.utils.sheet_to_json(worksheet, {header: 1}) as any[][];

          const filteredData = jsonData.filter((row: any[]) => {
            return row.some(cell => cell !== null && cell !== undefined && cell !== '');
          });
          for (let i = 0; i < filteredData.length; i++) {
            for (let j = 0; j < filteredData[i].length; j++) {
              if (filteredData[i][j] === null || filteredData[i][j] === undefined) {
                filteredData[i][j] = '';
              }
            }
          }
          if (scheduling) {

            const stopReadingIndex = filteredData.findIndex(row => row.some(cell => cell === '停止读取')); // 找到停止读取的行
            if (stopReadingIndex !== -1) {
              filteredData.splice(stopReadingIndex);
            }

            const onlineScheduleIndex = filteredData[0].indexOf('上线排期');
            if (onlineScheduleIndex !== -1) {
              for (let i = 1; i < filteredData.length; i++) {
                const cell = filteredData[i][onlineScheduleIndex];
                if (cell == '' || isNaN(Number(cell))) {
                  filteredData.splice(i, 1);
                  i--;
                } else {
                  filteredData[i][onlineScheduleIndex] = Number(cell);
                  const date = new Date((cell - 25569) * 86400 * 1000);

                  if (date >= dateRange.value[0] && date <= dateRange.value[1]) {
                    const year = date.getFullYear();
                    const month = date.getMonth() + 1;
                    const day = date.getDate();
                    const monthStr = month < 10 ? `0${month}` : `${month}`;
                    const dayStr = day < 10 ? `0${day}` : `${day}`;
                    filteredData[i][onlineScheduleIndex] = `${year}-${monthStr}-${dayStr}`;
                  } else {
                    filteredData.splice(i, 1);
                    i--;
                  }
                }
              }
            }
          }

          for (let i = 0; i < filteredData[0].length; i++) {
            if (filteredData.every(row => row[i] === null || row[i] === undefined)) {
              filteredData.forEach(row => row.splice(i, 1));
              i--;
            }
          }

          const encodedData = filteredData.map(row =>
              row.map(cell => typeof cell === 'string' ?
                  new TextDecoder('utf-8').decode(new TextEncoder().encode(cell)) : cell)
          );

          const tableData = encodedData.slice(1).map(row => {
            const obj: { [key: string]: any } = {};
            encodedData[0].forEach((key, index) => {
              obj[key] = String(row[index]).toString().substring(0, 40);
              if (String(obj[key]).toString() === 'undefined') {
                obj[key] = '';
              }
            });
            return obj;
          });

          return {
            sheetName: sheetName,
            sheetHeaders: encodedData[0].map(header => ({prop: header, label: header})),
            sheetData: encodedData.slice(1),
            tableData: tableData,
            gameName: gameName,
            releaseDate: releaseDate,
            parent: parent,
            scheduling: scheduling
          };
        }).filter(sheet => sheet !== null);

        unloadedSheetData.value = unloadedSheets;
        if (unloadedSheets.length > 0) {
          ElMessage({
            message: `未加载的表格:<br><br>${unloadedSheets.map(sheet => `----${sheet}`).join('<br>')}`,
            type: 'warning',
            duration: 10000,
            dangerouslyUseHTMLString: true
          });
        }
        sheets.sort((a: any, b: any) => {
          if (a.scheduling && !b.scheduling) {
            return -1;
          } else if (!a.scheduling && b.scheduling) {
            return 1;
          } else {
            return a.releaseDate.localeCompare(b.releaseDate);
          }
        });

        sheetData.value = sheets;
        fileData.value = sheets;

        schedulingData.value = schedulingDataIn;
      };
      reader.readAsArrayBuffer(file);
    };

    const uploadToServer = async () => {
      if (fileData.value) {
        const loadingMessage = ElMessage({
          message: '正在上传中，请稍候（离开页面不影响上传结果）...',
          type: 'info',
          showClose: false,
          duration: 0,
        });
        const uploadButton = document.querySelector('.upload-button');
        if (uploadButton) {
          (uploadButton as HTMLButtonElement).disabled = true;
        }
        try {
          const response = await UploadDDDD({sheets: filteredSheetData.value, schedulingData: schedulingData.value});
          ElMessage({
            message: '上传成功',
            type: 'success',
            duration: 5000
          });
          sheetData.value = [];
          fileData.value = null;
          schedulingData.value = null;
          unloadedSheetData.value = [];
          tabsWrapper.value?.scrollTo(0, 0);
          activeTab.value = '0';
          const uploadInput = document.querySelector('.el-upload__input');
          if (uploadInput) {
            (uploadInput as HTMLInputElement).value = '';
          }
          const blob = new Blob([response.message], {type: 'text/plain'});
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.download = `上传日志_${new Date().getTime()}.log`;
          a.href = url;
          a.click();
          window.URL.revokeObjectURL(url);
        } catch (error) {
          console.error('上传失败:', error);
          ElMessage({
            message: '上传失败，请重试',
            type: 'error',
            duration: 5000
          });
        }
        if (uploadButton) {
          (uploadButton as HTMLButtonElement).disabled = false;
        }
        loadingMessage.close();
      } else {
        ElMessage({
          message: '请先上传文件',
          type: 'warning',
          duration: 5000
        });
      }
    };

    return {
      sheetData,
      activeTab,
      handleFileRead,
      beforeRemove,
      uploadToServer,
      handleRemove,
      tabsWrapper,
      dateRange,
      defaultTimeRange,
      filteredSheetData
    };
  },
});
</script>
