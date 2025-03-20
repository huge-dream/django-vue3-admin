<template>
	<div class="user-info-head" @click="editCropper()">
		<el-avatar :size="100" :src="getBaseURL(options.img)" />
		<el-dialog :title="title" v-model="dialogVisiable" width="600px" append-to-body @opened="modalOpened" @close="closeDialog">
			<el-row>
				<el-col class="flex justify-center">
					<vue-cropper
						ref="cropper"
						:img="options.img"
						:info="true"
						:autoCrop="options.autoCrop"
						:autoCropWidth="options.autoCropWidth"
						:autoCropHeight="options.autoCropHeight"
						:fixedBox="options.fixedBox"
						:outputType="options.outputType"
						@realTime="realTime"
						:centerBox="true"
						v-if="visible"
						class="cropper"
					/>
				</el-col>
			</el-row>
			<br />
			<el-row class="flex justify-center">
				<el-col :lg="2" :md="2">
					<el-upload action="#" :http-request="requestUpload" :show-file-list="false" :before-upload="beforeUpload">
						<el-button type="success">
							选择
							<el-icon class="el-icon--right"><Plus /></el-icon>
						</el-button>
					</el-upload>
				</el-col>
				<el-col :lg="{ span: 1, offset: 2 }" :md="2">
					<el-button icon="RefreshLeft" @click="rotateLeft()"></el-button>
				</el-col>
				<el-col :lg="{ span: 1, offset: 2 }" :md="2">
					<el-button icon="RefreshRight" @click="rotateRight()"></el-button>
				</el-col>
				<el-col :lg="{ span: 2, offset: 2 }" :md="2">
					<el-button type="primary" @click="uploadImg()">更新头像</el-button>
				</el-col>
			</el-row>
		</el-dialog>
	</div>
</template>

<script setup>
import 'vue-cropper/dist/index.css';
import { VueCropper } from 'vue-cropper';
import { useUserInfo } from '/@/stores/userInfo';
import { getCurrentInstance, nextTick, reactive, ref, computed, onMounted, defineExpose } from 'vue';
import { base64ToFile } from '/@/utils/tools';
import headerImage from "/@/assets/img/headerImage.png";
import {getBaseURL} from "/@/utils/baseUrl";
const userStore = useUserInfo();
const { proxy } = getCurrentInstance();

const visible = ref(false);
const title = ref('修改头像');
const emit = defineEmits(['uploadImg']);
const props = defineProps({
	modelValue: {
		type: Boolean,
		default: false,
		required: true,
	},
});
const dialogVisiable = computed({
	get() {
		return props.modelValue;
	},
	set(newVal) {
		emit('update:modelValue', newVal);
	},
});

//图片裁剪数据
const options = reactive({
	img: userStore.userInfos.avatar || headerImage, // 裁剪图片的地址
	fileName: '',
	autoCrop: true, // 是否默认生成截图框
	autoCropWidth: 200, // 默认生成截图框宽度
	autoCropHeight: 200, // 默认生成截图框高度
	fixedBox: true, // 固定截图框大小 不允许改变
	outputType: 'png', // 默认生成截图为PNG格式
});

/** 编辑头像 */
function editCropper() {
	dialogVisiable.value = true;
}
/** 打开弹出层结束时的回调 */
function modalOpened() {
	nextTick(() => {
		visible.value = true;
	});
}
/** 覆盖默认上传行为 */
function requestUpload() {}
/** 向左旋转 */
function rotateLeft() {
	proxy.$refs.cropper.rotateLeft();
}
/** 向右旋转 */
function rotateRight() {
	proxy.$refs.cropper.rotateRight();
}
/** 图片缩放 */
function changeScale(num) {
	num = num || 1;
	proxy.$refs.cropper.changeScale(num);
}
/** 上传预处理 */
function beforeUpload(file) {
	if (file.type.indexOf('image/') == -1) {
		proxy.$modal.msgError('文件格式错误，请上传图片类型,如：JPG，PNG后缀的文件。');
	} else {
		const reader = new FileReader();
		reader.readAsDataURL(file);
		reader.onload = () => {
			options.img = reader.result;
			options.fileName = file.name;
		};
	}
}
/** 上传图片 */
function uploadImg() {
	// 获取截图的 base64 数据
	proxy.$refs.cropper.getCropData((data) => {
		let img = new Image();
		img.src = data;
		img.onload = async () => {
			let _data = compress(img);
			const imgFile = base64ToFile(_data, options.fileName);
			emit('uploadImg', imgFile);
		};
	});
}
// 压缩图片
function compress(img) {
	let canvas = document.createElement('canvas');
	let ctx = canvas.getContext('2d');
	// let initSize = img.src.length;
	let width = img.width;
	let height = img.height;
	canvas.width = width;
	canvas.height = height;
	// 铺底色
	ctx.fillStyle = '#fff';
	ctx.fillRect(0, 0, canvas.width, canvas.height);
	ctx.drawImage(img, 0, 0, width, height);
	// 进行压缩
	let ndata = canvas.toDataURL('image/jpeg', 0.8);
	return ndata;
}

/** 关闭窗口 */
function closeDialog() {
	options.visible = false;
	options.img = userStore.userInfos.avatar;
}

const updateAvatar = (img) => {
	options.img = img;
};

defineExpose({
	updateAvatar,
	editCropper
});
</script>

<style lang="scss" scoped>
.user-info-head {
	position: relative;
	display: inline-block;
}

.user-info-head:hover:after {
	content: '修改头像';
	position: absolute;
	text-align: center;
	left: 0;
	right: 0;
	top: 0;
	bottom: 0;
	color: #000000;
	font-size: 20px;
	font-style: normal;
	cursor: pointer;
	line-height: 110px;
}
.cropper {
	height: 400px;
	width: 400px;
}
</style>
