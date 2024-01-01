import {defineStore} from "pinia";
import {request} from "/@/utils/service";
import XEUtils from "xe-utils";
import {toRaw} from 'vue'
export const useDeptInfoStore = defineStore('deptInfo', {
    state:()=>(
        {
            list:[],
            tree:[],
        }
    ),
    actions:{
      async requestDeptInfo() {
            // 请求部门信息
            const ret = await request({
                url: '/api/system/dept/all_dept/'
            })
            this.list = ret.data
            this.tree = XEUtils.toArrayTree(ret.data,{parentKey:'parent',strict:true})
        },
        async getDeptById(id:any){

        },
        async getParentDeptById(id: any){
            const tree = toRaw(this.tree)
            const obj =  XEUtils.findTree(tree, item => item.id == id)
            return  obj
        }
    }
})
