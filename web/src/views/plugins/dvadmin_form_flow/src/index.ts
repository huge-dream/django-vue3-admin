// 导入各个组件
import DVAFormDesigner from './components/DVAFormDesigner.vue'

// 把组件保存到一个数组中
const components = [
    DVAFormDesigner
]

// 定义 install 方法
const install = function (Vue) {

    if (install.installed) return
    install.installed = true
    // 遍历组件列表并注册全局组件
    components.map(component => {
        Vue.component(component.name, component) //component.name 此处使用到组件vue文件中的 name 属性
    })
}

if (typeof window !== 'undefined' && window.Vue) {
    install(window.Vue)
}

export default {
    // 导出的对象必须具备一个 install 方法
    install,
    // 组件列表
    ...components
}
