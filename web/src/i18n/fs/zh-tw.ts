// Fast-crud zh-tw locale (traditional Chinese)
export default {
  name: "zh-tw",
  fs: {
    component: {
      select: {
        placeholder: "請選擇"
      }
    },
    addForm: { title: "新增" },
    editForm: { title: "編輯" },
    viewForm: { title: "查看" },
    rowHandle: {
      title: "操作",
      remove: {
        text: "刪除",
        confirmTitle: "刪除提示",
        confirmMessage: "您確定要刪除該記錄嗎？",
        success: "刪除成功！",
        confirmText: "確定",
        cancelText: "取消"
      },
      copy: {
        text: "複製"
      },
      edit: {
        text: "編輯"
      },
      view: {
        text: "查看"
      }
    },
    form: {
      cancel: "取消",
      ok: "確定",
      reset: "重設",
      saveRemind: {
        title: "提示",
        content: "表單數據有變更，是否保存",
        cancel: "不保存",
        ok: "保存"
      },
      copy: "複製",
      paste: "貼上",
      copySuccess: "表單數據已複製，您可以在新增對話框中貼上"
    },
    actionbar: { add: "新增" },
    toolbar: {
      columnFilter: {
        title: "欄位設定",
        fixed: "固定",
        order: "排序",
        reset: "還原",
        confirm: "確定",
        unnamed: "未命名"
      },
      search: { title: "查詢顯示" },
      refresh: { title: "重新整理" },
      compact: { title: "緊湊模式" },
      export: { title: "導出" },
      columns: { title: "欄位設定" }
    },
    search: {
      container: {
        collapseButton: {
          text: {
            collapse: "收起",
            expand: "展開"
          }
        }
      },
      search: { text: "查詢" },
      reset: { text: "重設" },
      error: {
        message: "查詢表單校驗失敗"
      }
    },
    pagination: {
      showTotal: "共 {0} 條"
    },
    date: {
      formatter: { to: "至" }
    },
    extends: {
      tableSelect: {
        view: "查看",
        select: "選擇",
        ok: "確定",
        cancel: "取消"
      },
      cropper: {
        title: "圖片裁剪",
        preview: "預覽",
        reChoose: "重新選擇",
        flipX: "左右翻轉",
        flipY: "上下翻轉",
        reset: "重設",
        cancel: "取消",
        confirm: "確定",
        chooseImage: "+ 選擇圖片",
        onlySupport: "僅支援",
        sizeLimit: "大小不能超過",
        sizeNoLimit: "大小不限制"
      },
      fileUploader: {
        text: "文件上傳",
        limitTip: "文件數量不能超過 {0}",
        sizeLimitTip: "文件大小不能超過 {0}，當前大小：{1}",
        loadError: "圖片載入失敗",
        pixelLimitTip: "圖片像素尺寸不能超過 寬:{0}，高:{1}",
        hasUploading: "還有文件正在上傳，請等待上傳完成，或刪除它"
      }
    }
  }
} as any;
