// 定義內容
export default {
    message: {
        pages: {
            fileList: {
                table: {
                    columns: {
                        index: '序號',
                        keyword: '關鍵詞',
                        name: '文件名稱',
                        preview: '預覽',
                        url: '文件地址',
                        md5sum: '文件MD5',
                        mimeType: '文件類型(MIME)',
                        fileType: '文件類型',
                        size: '文件大小',
                        uploadMethod: '上傳方式',
                        createTime: '創建時間',
                    },
                },
                form: {
                    keywordPlaceholder: '請輸入關鍵詞',
                    namePlaceholder: '請輸入文件名稱',
                    fileTypePlaceholder: '請選擇文件類型',
                },
                fileType: {
                    image: '圖片',
                    video: '視頻',
                    audio: '音頻',
                    document: '文檔',
                    other: '其他',
                    unknown: '未知類型',
                },
                tabs: {
                    image: '圖片',
                    video: '視頻',
                    audio: '音頻',
                    other: '其他',
                },
                uploadMethod: {
                    default: '預設上傳',
                    selector: '檔案選擇器上傳',
                },
                buttons: {
                    upload: '上傳',
                    add: '新增',
                    edit: '編輯',
                    delete: '刪除',
                },
                size: {
                    bytes: 'b',
                    kilobytes: 'Kb',
                    megabytes: 'Mb',
                },
            },
        },
    },
};
