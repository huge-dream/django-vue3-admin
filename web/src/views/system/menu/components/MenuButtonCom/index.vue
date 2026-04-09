<template>
	<div class="menu-btn-com" :style="{ height: 'calc(72vh - 44px)' }">
		<fs-crud ref="crudRef" v-bind="crudBinding" style="height: 100%">
			<template #pagination-right>
				<el-text type="info" size="small">{{ t('message.pages.menu.buttons.totalCount', { count: totalCount }) }}</el-text>
			</template>
		</fs-crud>
	</div>
</template>

<script lang="ts" setup>
import { computed, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useFs } from '@fast-crud/fast-crud';
import { createCrudOptions } from './crud';
import { MenuTreeItemType } from '../../types';
import { ElMessage, ElMessageBox } from 'element-plus';
import XEUtils from 'xe-utils';
import { BatchDelete } from './api';
import { Delete } from '@element-plus/icons-vue';
import { useThemeConfig } from '/@/stores/themeConfig';
import { storeToRefs } from 'pinia';

const { themeConfig } = storeToRefs(useThemeConfig());

const { t } = useI18n();

let selectOptions: any = ref({ name: null });

const { crudRef, crudBinding, crudExpose, context,selectedRows } = useFs({ createCrudOptions, context: { selectOptions } });
const { doRefresh, setTableData } = crudExpose;

// 选中行的条数
const selectedRowsCount = computed(() => {
	return selectedRows.value.length;
});

// 总条数
const totalCount = computed(() => {
	return crudBinding.value?.pagination?.total || 0;
});

const handleRefreshTable = (record: MenuTreeItemType) => {
	if (!record.is_catalog && record.id) {
		selectOptions.value = record;
		doRefresh();
	} else {
		setTableData([]);
	}
};

defineExpose({ selectOptions, handleRefreshTable });
</script>

<style lang="scss" scoped>
.menu-btn-com {
	height: 100%;
	overflow: hidden;
	display: flex;
	flex-direction: column;
}
</style>
