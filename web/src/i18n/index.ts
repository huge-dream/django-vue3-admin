import { createI18n } from 'vue-i18n';
import pinia from '/@/stores/index';
import { storeToRefs } from 'pinia';
import { useThemeConfig } from '/@/stores/themeConfig';

// element plus 自带国际化
import enLocale from 'element-plus/es/locale/lang/en';
import zhcnLocale from 'element-plus/es/locale/lang/zh-cn';
import zhtwLocale from 'element-plus/es/locale/lang/zh-tw';

// fast-crud 国际化
import enFsLocale from '@fast-crud/fast-crud/dist/locale/lang/en';
import zhcnFsLocale from '@fast-crud/fast-crud/dist/locale/lang/zh-cn';
import zhcnFsTwLocale from './fs/zh-tw';

// 定义变量内容
const messages = {};
const element = { en: enLocale, 'zh-cn': zhcnLocale, 'zh-tw': zhtwLocale };
const itemize: Record<string, any[]> = { en: [], 'zh-cn': [], 'zh-tw': [] };
const modules: Record<string, any> = import.meta.glob('./**/*.ts', { eager: true });

// 对自动引入的 modules 进行分类 en、zh-cn、zh-tw
// glob 返回路径如: ./pages/login/zh-cn.ts
// 提取语言代码: 按 / 分割，取最后一段去掉 .ts
for (const path in modules) {
	const withoutExt = path.replace(/^\.\//, '').replace(/\.ts$/, '');
	const segs = withoutExt.split('/');
	const lang = segs[segs.length - 1];
	if (itemize[lang]) {
		itemize[lang].push(modules[path].default);
	}
}

// 合并数组对象（深度合并 — 深层 key 冲突时后一个文件的 value 覆盖前一个的 value）
function isObject(val: unknown): val is Record<string, any> {
	return val !== null && typeof val === 'object' && !Array.isArray(val);
}

function deepMerge(target: Record<string, any>, ...sources: Record<string, any>[]): Record<string, any> {
	for (const source of sources) {
		for (const key in source) {
			if (isObject(target[key]) && isObject(source[key])) {
				deepMerge(target[key], source[key]);
			} else {
				target[key] = source[key];
			}
		}
	}
	return target;
}

function mergeArrObj(list: any[], key: string) {
	let obj: Record<string, any> = {};
	list[key].forEach((i: Record<string, any>) => {
		deepMerge(obj, i);
	});
	return obj;
}

// fast-crud 原始语言标识 -> 项目语言标识映射
const fsLocaleMap: Record<string, any> = {
    'zh-cn': zhcnFsLocale,
    'en': enFsLocale,
    'zh-tw': zhcnFsTwLocale,
};

for (const key in itemize) {
	messages[key] = {
		name: key,
		el: element[key].el,
		...mergeArrObj(itemize, key),
		// fast-crud 内部组件的国际化（search/reset 按钮、操作列、列设置等）
		...fsLocaleMap[key],
	};
}

// 读取 pinia 默认语言
const stores = useThemeConfig(pinia);
const { themeConfig } = storeToRefs(stores);

// 导出语言国际化
export const i18n = createI18n({
	legacy: false,
	silentTranslationWarn: false,
	missingWarn: true,
	silentFallbackWarn: false,
	fallbackWarn: false,
	locale: themeConfig.value.globalI18n,
	fallbackLocale: ['zh-CN', 'en', 'zh-TW'],
	messages,
});
