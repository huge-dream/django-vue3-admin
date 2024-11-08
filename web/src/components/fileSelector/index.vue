<template>
	<el-select v-model="data" suffix-icon="arrow-down" clearable :multiple="props.multiple" placeholder="请选择文件"
		@click="selectVisiable = true" @clear="selectedInit" @remove-tag="selectedInit">
		<el-option v-for="item, index in listAllData" :key="index" :value="item.id" :label="item.name" />
	</el-select>
	<el-dialog v-model="selectVisiable" :draggable="false" width="50%" :align-center="false"
		@open="if (listData.length === 0) listRequest();">
		<template #header>
			<span class="el-dialog__title">文件选择</span>
			<el-divider style="margin: 0;" />
		</template>
		<div style="padding: 4px;">
			<el-tabs v-model="tabsActived" :type="props.tabsType" :stretch="true" @tab-change="handleTabChange">
				<el-tab-pane v-if="props.tabsShow & SHOW.IMAGE" :name="0" label="图片" />
				<el-tab-pane v-if="props.tabsShow & SHOW.VIDEO" :name="1" label="视频" />
				<el-tab-pane v-if="props.tabsShow & SHOW.AUDIO" :name="2" label="音频" />
				<el-tab-pane v-if="props.tabsShow & SHOW.OTHER" :name="3" label="其他" />
			</el-tabs>
			<el-row justify="space-between" class="headerBar">
				<el-span :span="16">
					<el-input v-model="filterForm.name" :placeholder="`请输入${TypeLabel[tabsActived]}名`" prefix-icon="search"
						clearable @change="listRequest" />
					<div>
						<el-tag v-if="props.multiple" type="primary" effect="light">
							一共选中&nbsp;{{ data?.length || 0 }}&nbsp;个文件
						</el-tag>
					</div>
				</el-span>
				<el-span :span="8">
					<el-button type="default" circle icon="refresh" @click="listRequest" />
					<!-- 这里 show-file-list 和 clearFiles 一起使用确保不会显示上传列表 -->
					<el-upload ref="uploadRef" :action="getBaseURL() + 'api/system/file/'" :multiple="false"
						:data="{ upload_method: 1 }" :drag="false" :show-file-list="false" :accept="AcceptList[tabsActived]"
						:on-success="() => { listRequest(); listRequestAll(); uploadRef.clearFiles(); }">
						<el-button type="primary" icon="plus">上传{{ TypeLabel[tabsActived] }}</el-button>
					</el-upload>
				</el-span>
			</el-row>
			<el-empty v-if="!listData.length" description="无内容，请上传"
				style="width: 100%; height: calc(50vh); margin-top: 24px; padding: 4px;" />
			<div ref="listContainerRef" class="listContainer" v-else>
				<div v-for="item in listData" :style="{ width: (props.itemSize || 100) + 'px' }" :key="item.id"
					@click="onItemClick($event)" :data-id="item.id">
					<FileItem :fileData="item" />
				</div>
			</div>
			<div class="listPaginator">
				<el-pagination background size="small" layout="total, sizes, prev, pager, next" :total="pageForm.total"
					v-model:page-size="pageForm.limit" :page-sizes="[10, 20, 30, 40, 50]" v-model:current-page="pageForm.page"
					:hide-on-single-page="false" @change="handlePageChange" />
			</div>
		</div>
		<template #footer>
			<el-button type="default" @click="selectVisiable = false">取消</el-button>
			<el-button type="primary" @click="selectVisiable = false">确定</el-button>
		</template>
	</el-dialog>
</template>

<script setup lang="ts">
import { useUi, UserPageQuery, AddReq, EditReq, DelReq } from '@fast-crud/fast-crud';
import { ref, reactive, defineProps, PropType, watch, onMounted, nextTick } from 'vue';
import { getBaseURL } from '/@/utils/baseUrl';
import { request } from '/@/utils/service';
import { SHOW } from './types';
import FileItem from './fileItem.vue';

const TypeLabel = ['图片', '视频', '音频', '文件']
const AcceptList = ['image/*', 'video/*', 'audio/*', ''];
const props = defineProps({
	modelValue: {},
	tabsType: { type: Object as PropType<'' | 'card' | 'border-card'>, default: '' },
	// 1000图片 100视频 10音频 1 其他 控制tabs的显示
	tabsShow: { type: Number, default: SHOW.ALL },
	itemSize: { type: Number, default: 100 },
	multiple: { type: Boolean, default: false },
} as any);
const selectVisiable = ref<boolean>(false);
const tabsActived = ref<number>(0);
const fileApiPrefix = '/api/system/file/';
const fileApi = {
	GetList: (query: UserPageQuery) => request({ url: fileApiPrefix, method: 'get', params: query }),
	GetAll: () => request({ url: fileApiPrefix + 'get_all/' }),
	AddObj: (obj: AddReq) => request({ url: fileApiPrefix, method: 'post', data: obj }),
	UpdateObj: (obj: EditReq) => request({ url: fileApiPrefix + obj.id + '/', method: 'put', data: obj }),
	DelObj: (id: DelReq) => request({ url: fileApiPrefix + id + '/', method: 'delete', data: { id } }),
};
// 过滤表单
const filterForm = reactive({ name: '' });
// 分页表单
const pageForm = reactive({ page: 1, limit: 10, total: 0 });
// 展示的数据列表
const listData = ref<any[]>([]);
const listAllData = ref<any[]>([]);
const listRequest = async () => {
	let res = await fileApi.GetList({ page: pageForm.page, limit: pageForm.limit, file_type: tabsActived.value, ...filterForm });
	listData.value = res.data;
	pageForm.total = res.total;
	pageForm.page = res.page;
	pageForm.limit = res.limit;
	selectedInit();
};
const listRequestAll = async () => { let res = await fileApi.GetAll(); listAllData.value = res.data; };
// tab改变时触发
const handleTabChange = (name: string) => { pageForm.page = 1; listRequest(); };
// 分页器改变时触发
const handlePageChange = (currentPage: number, pageSize: number) => { pageForm.page = currentPage; pageForm.limit = pageSize; listRequest(); };
// 选择的行为
const listContainerRef = ref<any>();
const onItemClick = async (e: MouseEvent) => {
	let target = e.target as HTMLElement;
	let flat = 0;  // -1删除 0不变 1添加
	while (!target.dataset.id) target = target.parentElement as HTMLElement;
	let fileId = Number(target.dataset.id);
	if (props.multiple) {
		if (target.classList.contains('active')) {
			target.classList.remove('active');
			flat = -1;
		} else {
			target.classList.add('active');
			flat = 1;
		}
		if (data.value) {
			if (flat === 1) data.value.push(fileId);
			else data.value.splice(data.value.indexOf(fileId), 1);
		}
		else data.value = [fileId];
		// 去重排序，<降序，>升序
		data.value = Array.from(new Set(data.value)).sort();
	} else {
		for (let i of listContainerRef.value?.children) {
			(i as HTMLElement).classList.remove('active');
		}
		target.classList.add('active');
		data.value = fileId;
	}
	onDataChange(data.value);
};
// 每次列表刷新都得更新一下选择状态，因为所有标签页共享列表
const selectedInit = async () => {
	await nextTick();
	for (let i of (listContainerRef.value?.children || [])) {
		i.classList.remove('active');
		let fid = Number((i as HTMLElement).dataset.id);
		if (props.multiple) {
			if (data.value?.includes(fid)) i.classList.add('active');
		} else {
			if (fid === data.value) i.classList.add('active');
		}
	}
};
const uploadRef = ref<any>();
// 清空状态
const clear = () => {
	filterForm.name = '';
	pageForm.page = 1;
	pageForm.limit = 10;
	pageForm.total = 0;
	listData.value = [];
	// all数据不能清，因为all只会在挂载的时候赋值一次
	// listAllData.value = [];
	data.value = null;
};


// fs-crud部分
const data = ref<any>();
const emit = defineEmits(['update:modelValue']);
watch(() => props.modelValue, (val) => { data.value = val; }, { immediate: true });
const { ui } = useUi();
const formValidator = ui.formItem.injectFormItemContext();
const onDataChange = (value: any) => {
	emit('update:modelValue', value);
	formValidator.onChange();
	formValidator.onBlur();
};
defineExpose({ data, onDataChange, selectVisiable, clear });

onMounted(() => listRequestAll());
</script>

<style scoped>
.headerBar>* {
	display: flex;
	justify-content: space-between;
	gap: 12px;
}

.listContainer {
	display: grid;
	justify-items: center;
	grid-template-columns: repeat(4, 1fr);
	grid-auto-rows: min-content;
	grid-gap: 36px;
	margin-top: 24px;
	padding: 8px;
	height: calc(50vh);
	overflow-y: auto;
	scrollbar-width: thin;
}

.listContainer>* {
	aspect-ratio: 1 / 1;
	/* border: 1px solid rgba(0, 0, 0, .1); */
	/* div阴影，2px范围，均匀投影，0偏移 */
	box-shadow: 0 0 4px rgba(0, 0, 0, .2);
	cursor: pointer;
	border-radius: 8px;
	overflow: hidden;
}

.active {
	box-shadow: 0 0 8px var(--el-color-primary);
}

.listPaginator {
	display: flex;
	justify-content: flex-end;
	justify-items: center;
	padding-top: 24px;
}
</style>