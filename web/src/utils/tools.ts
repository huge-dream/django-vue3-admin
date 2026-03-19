/**
 * @description 安全地解析 json 字符串
 * @param {String} jsonString 需要解析的 json 字符串
 * @param {String} defaultValue 默认值
 */
import { uiContext } from '@fast-crud/fast-crud';

export function parse(jsonString = '{}', defaultValue = {}) {
	let result = defaultValue;
	try {
		result = JSON.parse(jsonString);
	} catch (error) {
		console.log(error);
	}
	return result;
}

/**
 * @description 接口请求返回
 * @param {Any} data 返回值
 * @param {String} msg 状态信息
 * @param {Number} code 状态码
 */
export function response(data = {}, msg = '', code = 0) {
	return [200, { code, msg, data }];
}

/**
 * @description 接口请求返回 正确返回
 * @param {Any} data 返回值
 * @param {String} msg 状态信息
 */
export function responseSuccess(data = {}, msg = '成功') {
	return response(data, msg);
}

/**
 * @description 接口请求返回 错误返回
 * @param {Any} data 返回值
 * @param {String} msg 状态信息
 * @param {Number} code 状态码
 */
export function responseError(data = {}, msg = '请求失败', code = 500) {
	return response(data, msg, code);
}

/**
 * @description 记录和显示错误
 * @param {Error} error 错误对象
 */
export function errorLog(error: any, notification = true) {
	// 打印到控制台
	console.error(error);
	// 显示提示
	if (notification) {
		uiContext.get().notification.error({ message: error.message });
	}
}

/**
 * @description 创建一个错误
 * @param {String} msg 错误信息
 */
export function errorCreate(msg: any, notification = true) {
	const error = new Error(msg);
	errorLog(error, notification);
	// throw error;
}

/**
 * @description base64转file
 * @param {String} base64 base64字符串
 * @param {String} fileName 文件名
 */
export function base64ToFile(base64: any, fileName: string) {
	// 将base64按照 , 进行分割 将前缀  与后续内容分隔开
	let data = base64.split(',');
	// 利用正则表达式 从前缀中获取图片的类型信息（image/png、image/jpeg、image/webp等）
	let type = data[0].match(/:(.*?);/)[1];
	// 从图片的类型信息中 获取具体的文件格式后缀（png、jpeg、webp）
	let suffix = type.split('/')[1];
	// 使用atob()对base64数据进行解码  结果是一个文件数据流 以字符串的格式输出
	const bstr = window.atob(data[1]);
	// 获取解码结果字符串的长度
	let n = bstr.length;
	// 根据解码结果字符串的长度创建一个等长的整形数字数组
	// 但在创建时 所有元素初始值都为 0
	const u8arr = new Uint8Array(n);
	// 将整形数组的每个元素填充为解码结果字符串对应位置字符的UTF-16 编码单元
	while (n--) {
		// charCodeAt()：获取给定索引处字符对应的 UTF-16 代码单元
		u8arr[n] = bstr.charCodeAt(n);
	}
	// 利用构造函数创建File文件对象
	// new File(bits, name, options)
	const file = new File([u8arr], `${fileName}.${suffix}`, {
		type: type,
	});
	// 将File文件对象返回给方法的调用者
	return file;
}
