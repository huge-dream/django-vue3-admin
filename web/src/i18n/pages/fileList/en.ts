// Define content
export default {
    message: {
        pages: {
            fileList: {
                table: {
                    columns: {
                        index: 'No.',
                        keyword: 'Keyword',
                        name: 'File Name',
                        preview: 'Preview',
                        url: 'File URL',
                        md5sum: 'MD5',
                        mimeType: 'MIME Type',
                        fileType: 'File Type',
                        size: 'File Size',
                        uploadMethod: 'Upload Method',
                        createTime: 'Create Time',
                    },
                },
                form: {
                    keywordPlaceholder: 'Enter keyword',
                    namePlaceholder: 'Enter file name',
                    fileTypePlaceholder: 'Select file type',
                },
                fileType: {
                    image: 'Image',
                    video: 'Video',
                    audio: 'Audio',
                    document: 'Document',
                    other: 'Other',
                    unknown: 'Unknown',
                },
                tabs: {
                    image: 'Image',
                    video: 'Video',
                    audio: 'Audio',
                    other: 'Other',
                },
                uploadMethod: {
                    default: 'Default Upload',
                    selector: 'File Selector Upload',
                },
                buttons: {
                    upload: 'Upload',
                    add: 'Add',
                    edit: 'Edit',
                    delete: 'Delete',
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
