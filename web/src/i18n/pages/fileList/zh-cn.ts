// 定义内容
export default {
    message: {
        pages: {
            fileList: {
                table: {
                    columns: {
                        index: '序号',
                        keyword: '关键词',
                        name: '文件名称',
                        preview: '预览',
                        url: '文件地址',
                        md5sum: '文件MD5',
                        mimeType: '文件类型(MIME)',
                        fileType: '文件类型',
                        size: '文件大小',
                        uploadMethod: '上传方式',
                        createTime: '创建时间',
                    },
                },
                form: {
                    keywordPlaceholder: '请输入关键词',
                    namePlaceholder: '请输入文件名称',
                    fileTypePlaceholder: '请选择文件类型',
                },
                fileType: {
                    image: '图片',
                    video: '视频',
                    audio: '音频',
                    document: '文档',
                    other: '其他',
                    unknown: '未知类型',
                },
                tabs: {
                    image: '图片',
                    video: '视频',
                    audio: '音频',
                    other: '其他',
                },
                uploadMethod: {
                    default: '默认上传',
                    selector: '文件选择器上传',
                },
                buttons: {
                    upload: '上传',
                    add: '新增',
                    edit: '编辑',
                    delete: '删除',
                },
                size: {
                    bytes: 'B',
                    kilobytes: 'KB',
                    megabytes: 'MB',
                },
            },
        },
    },
};
