import * as api from './api';
import { CreateCrudOptionsProps, CreateCrudOptionsRet, dict, useCompute } from '@fast-crud/fast-crud';
const { compute } = useCompute();
import { shallowRef } from "vue";
import IconSelector from "/@/components/IconSelector/index.vue"
export default function ({ crudExpose }: CreateCrudOptionsProps): CreateCrudOptionsRet {
	const pageRequest = async (query) => {
		return await api.GetList(query);
	};
	const editRequest = async ({ form, row }) => {
		form.id = row.id;
		await api.UpdateObj(form);
		if (row.parent) {
			//刷新父节点的状态
			reloadTreeChildren(row.parent);
		}
	};
	const delRequest = async ({ row }:any) => {
		await api.DelObj(row.id);
		if (row.parent) {
			//刷新父节点的状态
			reloadTreeChildren(row.parent);
		}
	};

	const addRequest = async (context:any) => {
		const {form} = context;
		if(form.web_path===undefined||form.web_path===null){
			form.web_path='/'
		}
		return await api.AddObj(form);
	};

	//刷新父节点状态
	function reloadTreeChildren(parent:string|number) {
		const data = crudExpose.getBaseTableRef().store.states.treeData;
		if (data.value != null) {
			const item = data.value[parent];
			if (item != null) {
				item.loaded = false;
				item.expanded = false;
			}
		}
	}

	const createFilter = (queryString: string) => {
		return (file: any) => {
			return file.value.toLowerCase().indexOf(queryString.toLowerCase()) !== -1;
		};
	};

	// 获取组件地址
	const getCompoent = (queryString: string, cb: any) => {
		const files: any = import.meta.glob('@views/**/*.vue');
		let fileLists: Array<any> = [];
		Object.keys(files).forEach((queryString: string) => {
			fileLists.push({
				label: queryString.replace(/(\.\/|\.vue)/g, ''),
				value: queryString.replace(/(\.\/|\.vue)/g, ''),
			});
		});
		const results = queryString ? fileLists.filter(createFilter(queryString)) : fileLists;
		// 统一去掉/src/views/前缀
		results.forEach((val) => {
			val.label = val.label.replace('/src/views/', '');
			val.value = val.value.replace('/src/views/', '');
		});
		cb(results);
	};

	// 验证路由地址
	const { getFormData } = crudExpose;
	const validateWebPath = (rule: any, value: string, callback: Function) => {
		let pattern = /^\/.*?/;
		let patternUrl = /http(s)?:\/\/([\w-]+\.)+[\w-]+(\/[\w- .\/?%&=]*)?/;
		const reg = getFormData().is_link ? patternUrl.test(value) : pattern.test(value);
		if (reg) {
			callback();
		} else {
			callback(new Error('请输入正确的地址'));
		}
	};

	return {
		crudOptions: {
			request: {
				pageRequest,
				addRequest,
				editRequest,
				delRequest,
			},
			pagination: {
				show: false,
			},
			form: {
				labelWidth: '120px',
				row: { gutter: 20 },
				// group: {
				// 	groupType: 'tabs', //collapse， tabs
				// 	accordion: false,
				// 	groups: {
				// 		catalog: {
				// 			label: '目录',
				// 			icon: 'el-icon-goods',
				// 			columns: ['name', 'icon', 'sort', 'status'],
				// 		},
				// 		menu: {
				// 			label: '菜单',
				// 			icon: 'el-icon-price-tag',
				// 			columns: ['parent', 'name', 'icon', 'is_link', 'web_path', 'component', 'cache', 'visible', 'frame_out', 'sort', 'status'],
				// 		},
				// 		info: {
				// 			label: '按钮',
				// 			collapsed: true, //默认折叠
				// 			icon: 'el-icon-warning-outline',
				// 			columns: ['name', 'component'],
				// 		},
				// 	},
				// },
			},
			table: {
				lazy: true,
				load: async (row: any, treeNode: unknown, resolve: (date: any[]) => void) => {
					//懒加载，更新和删除后，需要刷新父节点的状态，见上方
					const obj = await api.GetChildren(row.id);
					resolve([...obj.data]);
				},
			},
			columns: {
				id: {
					title: 'ID',
					key: 'id',
					type: 'number',
					column: {
						width: 100,
					},
					form: {
						show: false,
					},
				},
				menu_type: {
					title: '类型',
					type: 'dict-radio',
					dict: dict({
						data: [
							{ label: '目录', value: 0 },
							{ label: '菜单', value: 1 },
							{ label: '按钮', value: 2 },
						],
					}),
					form: {
						value:0,
						valueChange({ form, value, getComponentRef }) {
							if (value) {
								getComponentRef("parent")?.reloadDict(); // 执行city的select组件的reloadDict()方法，触发“city”重新加载字典
							}
						}
					},
					column: {
						show: false,
					},
				},
				parent: {
					title: '父级',
					dict: dict({
						prototype: true,
						url({form}){
							if(form && form.menu_type===1){
								return '/api/system/menu/tree/?menu_type=0'
							}else{
								return `/api/system/menu/tree/?menu_type=1`
							}
							return undefined
						},
						label: 'name',
						value: 'id',
					}),
					type: 'dict-select',
					form: {
						show:compute(({form})=>{
							return [1,2].includes(form.menu_type);
						}),
						rules: [{ required: true, message: '必填项' }],
						component: {},
					},
					column: {
						show: false,
					},
				},
				name: {
					title: '名称',
					search: { show: true },
					type: 'text',
					form: {
						rules: [{ required: true, message: '请输入名称' }],
						component: {
							placeholder: '请输入名称',
						},
					},
				},
				icon: {
					title: '图标',
					form:{
						show:compute(({form})=>{
							return [0,1].includes(form.menu_type);
						}),
						component:{
							name: shallowRef(IconSelector),
							vModel: "modelValue",
						}
					},
					column: {
						component: {
							style: 'font-size:18px',
						},
					},
				},
				sort: {
					title: '排序',
					type: 'number',
					form: {
						value: 1,
						show:compute(({form})=>{
							return [0,1].includes(form.menu_type);
						}),
					},
				},
				is_link: {
					title: '外链接',
					type: 'dict-switch',
					dict: dict({
						data: [
							{ label: '是', value: true },
							{ label: '否', value: false },
						],
					}),
					form: {
						value: false,
						show:compute(({form})=>{
							return [1].includes(form.menu_type);
						}),
					},
				},
				web_path: {
					title: '路由地址',
					form: {
						show:compute(({form})=>{
							return [1].includes(form.menu_type);
						}),
						helper: compute(({ form }) => {
							return form.is_link ? '请输入http开头的地址' : '浏览器中url的地址,请以/开头';
						}),
						rules: [{ required: true, message: '请输入路由地址', validator: validateWebPath, trigger: 'blur' }],
						component: {
							placeholder: '请输入路由地址',
						},
					},
					column: {
						show: false,
					},
				},
				component: {
					title: compute(({ form }) => {
						return form.menu_type === 1 ? '组件地址' : '按钮权限值';
					}),
					form: {
						show: compute(({ form }) => {
							return [1,2].includes(form.menu_type)
						}),
						helper: compute(({ form }) => {
							return form.menu_type === 1 ? 'src/views下的文件夹地址' : '按钮权限值是唯一的标识';
						}),
						rules: [{ required: true, message: '请输入组件地址', trigger: 'blur' }],
						component: {
							style: {
								width: '100%',
							},
							disabled: compute(({ form }) => {
								if(form.is_link&&form.menu_type===1){
									form.component ="无"
									return form.is_link
								}
								form.component =null
								return false
							}),
							name: compute(({ form }) => {
								return [1,2].includes(form.menu_type)? 'el-autocomplete' : 'el-input';
							}),
							triggerOnFocus: false,
							fetchSuggestions: (query, cb) => {
								return getCompoent(query, cb);
							},
						},
					},
					column: {
						show: false,
					},
				},
				visible: {
					title: '侧边可见',
					search: { show: true },
					type: 'dict-radio',
					dict: dict({
						data: [
							{ label: '是', value: true },
							{ label: '否', value: false },
						],
					}),
					form: {
						value: true,
						show:compute(({form})=>{
							return [1].includes(form.menu_type)
						}),
					},
				},
				cache: {
					title: '是否缓存',
					search: { show: true },
					type: 'dict-radio',
					dict: dict({
						data: [
							{ label: '是', value: true },
							{ label: '否', value: false },
						],
					}),
					form: {
						value: false,
						show:compute(({form})=>{
							return [1].includes(form.menu_type)
						}),
					},
				},
				frame_out: {
					title: '主框架外展示',
					search: { show: true },
					type: 'dict-radio',
					dict: dict({
						data: [
							{ label: '是', value: true },
							{ label: '否', value: false },
						],
					}),
					form: {
						value: false,
						show:compute(({form})=>{
							return [1].includes(form.menu_type)
						}),
					},
				},
				status: {
					title: '状态',
					search: { show: true },
					type: 'dict-radio',
					dict: dict({
						data: [
							{ label: '启用', value: true },
							{ label: '禁用', value: false },
						],
					}),
					form: {
						value: true,
						show:compute(({form})=>{
							return [0,1].includes(form.menu_type);
						}),
					},
				},
			},
		},
	};
}
