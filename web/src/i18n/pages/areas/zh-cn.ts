// 定义内容
export default {
    message: {
        pages: {
            areas: {
                table: {
                    columns: {
                        index: '序号',
                        areaName: '区域名称',
                        areaCode: '区域编码',
                        parentArea: '上级区域',
                        sort: '排序',
                        status: '状态',
                        createTime: '创建时间',
                        actions: '操作',
                    },
                },
                form: {
                    areaName: '区域名称',
                    areaCode: '区域编码',
                    parentArea: '上级区域',
                    sort: '排序',
                    status: '状态',
                    areaNamePlaceholder: '请输入区域名称',
                    areaCodePlaceholder: '请输入区域编码',
                    sortPlaceholder: '请输入排序',
                },
                validation: {
                    areaNameRequired: '区域名称必填',
                    areaNameMaxLength: '区域名称不能超过50个字符',
                    areaNameDuplicate: '区域名称已存在',
                    areaCodeRequired: '区域编码必填',
                    areaCodeMaxLength: '区域编码不能超过50个字符',
                    areaCodeFormat: '区域编码格式不正确',
                    areaCodeDuplicate: '区域编码已存在',
                },
                dialog: {
                    addArea: '新增区域',
                    editArea: '编辑区域',
                    deleteConfirm: '确定删除该区域吗？',
                },
                messages: {
                    addSuccess: '新增成功',
                    updateSuccess: '更新成功',
                    deleteSuccess: '删除成功',
                    deleteFailed: '删除失败',
                },
                buttons: {
                    add: '新增',
                    edit: '编辑',
                    delete: '删除',
                    save: '保存',
                    cancel: '取消',
                    query: '查询',
                    refresh: '刷新',
                    expandAll: '展开全部',
                    collapseAll: '收起全部',
                },
            },
        },
    },
};
