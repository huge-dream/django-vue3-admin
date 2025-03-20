// 引入fast-crud
import {FastCrud, useTypes} from '@fast-crud/fast-crud';

const {getType} = useTypes();
import '@fast-crud/fast-crud/dist/style.css';
import {setLogger} from '@fast-crud/fast-crud';
import {getBaseURL} from '/@/utils/baseUrl';
// element
import ui from '@fast-crud/ui-element';
import {request} from '/@/utils/service';
//扩展包
import {FsExtendsEditor, FsExtendsUploader } from '@fast-crud/fast-extends';
import '@fast-crud/fast-extends/dist/style.css';
import {successNotification} from '/@/utils/message';
import XEUtils from "xe-utils";
export default {
    async install(app: any, options: any) {
        // 先安装ui
        app.use(ui);
        // 然后安装FastCrud
        app.use(FastCrud, {
            //i18n, //i18n配置，可选，默认使用中文，具体用法请看demo里的 src/i18n/index.js 文件
            // 此处配置公共的dictRequest（字典请求）
            async dictRequest({dict,url}: any) {
                const {isTree} = dict
                //根据dict的url，异步返回一个字典数组
                return await request({url: url, params: dict.params || {}}).then((res: any) => {
                    if (isTree) {
                        return XEUtils.toArrayTree(res.data, {parentKey: 'parent'})
                    }
                    return res.data
                });
            },
            //公共crud配置
            commonOptions() {
                return {
                    request: {
                        //接口请求配置
                        //你项目后台接口大概率与fast-crud所需要的返回结构不一致，所以需要配置此项
                        //请参考文档http://fast-crud.docmirror.cn/api/crud-options/request.html
                        transformQuery: ({page, form, sort}: any) => {
                            if (sort.asc !== undefined) {
                                form['ordering'] = `${sort.asc ? '' : '-'}${sort.prop}`;
                            }
                            //转换为你pageRequest所需要的请求参数结构
                            return {page: page.currentPage, limit: page.pageSize, ...form};
                        },
                        transformRes: ({res}: any) => {
                            //将pageRequest的返回数据，转换为fast-crud所需要的格式
                            //return {records,currentPage,pageSize,total};
                            return {records: res.data, currentPage: res.page, pageSize: res.limit, total: res.total};
                        },
                    },
                    form: {
                        afterSubmit(ctx: any) {
                            const {res} = ctx
                            // 增加crud提示
                            if (res?.code == 2000) {
                                successNotification(ctx.res.msg);
                            }else{
                                return
                            }
                        },
                    },
                    /* search: {
                        layout: 'multi-line',
                        collapse: true,
                        col: {
                            span: 4,
                        },
                        options: {
                            labelCol: {
                                style: {
                                    width: '100px',
                                },
                            },
                        },
                    }, */
                };
            },
            logger: { off: { tableColumns: false } }
        });
        //富文本
        app.use(FsExtendsEditor, {
            wangEditor: {
                width: 300,
            },
        });
        // 文件上传
        app.use(FsExtendsUploader, {
            defaultType: "form",
            form: {
                action: `/api/system/file/`,
                name: "file",
                withCredentials: false,
                uploadRequest: async ({ action, file, onProgress }: { action: string; file: any; onProgress: Function }) => {
                    // @ts-ignore
                    const data = new FormData();
                    data.append("file", file);
                    return await request({
                        url: action,
                        method: "post",
                        timeout: 60000,
                        headers: {
                            "Content-Type": "multipart/form-data"
                        },
                        data,
                        onUploadProgress: (p: any) => {
                            onProgress({percent: Math.round((p.loaded / p.total) * 100)});
                        }
                    });
                },
                successHandle(ret: any) {
                    // 上传完成后的结果处理， 此处应返回格式为{url:xxx,key:xxx}
                    return {
                        url: getBaseURL(ret.data.url),
                        key: ret.data.id,
                        ...ret.data
                    };
                }
            },
                valueBuilder(context: any){
                    const { row, key } = context
                    return getBaseURL(row[key])
                }
        })

        setLogger({level: 'error'});
        // 设置自动染色
        const dictComponentList = ['dict-cascader', 'dict-checkbox', 'dict-radio', 'dict-select', 'dict-switch', 'dict-tree'];
        dictComponentList.forEach((val) => {
            getType(val).column.component.color = 'auto';
            getType(val).column.align = 'center';
        });
        // 设置placeholder 的默认值
        const placeholderComponentList = [
            {key: 'text', placeholder: "请输入"},
            {key: 'textarea', placeholder: "请输入"},
            {key: 'input', placeholder: "请输入"},
            {key: 'password', placeholder: "请输入"}
        ]
        placeholderComponentList.forEach((val) => {
            if (getType(val.key)?.search?.component) {
                getType(val.key).search.component.placeholder = val.placeholder;
            } else if (getType(val.key)?.search) {
                getType(val.key).search.component = {placeholder: val.placeholder};
            }
            if (getType(val.key)?.form?.component) {
                getType(val.key).form.component.placeholder = val.placeholder;
            } else if (getType(val.key)?.form) {
                getType(val.key).form.component = {placeholder: val.placeholder};
            }
            if (getType(val.key)?.column?.align) {
                getType(val.key).column.align = 'center'
            } else if (getType(val.key)?.column) {
                getType(val.key).column = {align: 'center'};
            } else if (getType(val.key)) {
                getType(val.key).column = {align: 'center'};
            }
        });
    },
};
