import { defineAsyncComponent, AsyncComponentLoader } from 'vue';
export let pluginsAll: any = [];
// 扫描插件目录并注册插件
export const scanAndInstallPlugins = (app: any) => {
	const components = import.meta.glob('./**/*.vue');
	const pluginNames = new Set();
	// 遍历对象并注册异步组件
	for (const [key, value] of Object.entries(components)) {
		const name = key.slice(key.lastIndexOf('/') + 1, key.lastIndexOf('.'));
		app.component(name, defineAsyncComponent(value as AsyncComponentLoader));
		const pluginsName = key.match(/\/([^\/]*)\//)?.[1];
		pluginNames.add(pluginsName);
	}
	pluginsAll = Array.from(pluginNames);
	console.table('已注册插件：', pluginsAll);
};
