import {App} from "vue/dist/vue";

const map = new WeakMap()
const ob = new ResizeObserver((entries) => {
    for(const  entry of entries){
        const handler = map.get(entry.target);
        handler && handler({
            width: entry.borderBoxSize[0].inlineSize,
            height: entry.borderBoxSize[0].blockSize
        });
    }
});
export function resizeObDirective(app: App){
    app.directive('resizeOb', {
        mounted(el,binding) {
            map.set(el,binding.value);
            ob.observe(el); // 监听目标元素
        },
        unmounted(el) {
            ob.unobserve(el); // 停止监听
        },
    })
}
