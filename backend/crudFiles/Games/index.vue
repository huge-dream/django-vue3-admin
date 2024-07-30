
<template>
    <fs-page>
        <fs-crud ref="crudRef" v-bind="crudBinding"></fs-crud>
    </fs-page>
</template>

<script lang="ts" setup name="Games ">
// Games Page - Auto-generated on 2024-05-20 15:28:49
import {ref, onMounted} from 'vue';
import {useFs} from '@fast-crud/fast-crud';
import {createCrudOptions} from './crud';
const {crudBinding, crudRef, crudExpose} = useFs({createCrudOptions});

// 页面打开后获取列表数据
onMounted(() => {
    crudExpose.doRefresh();
});
</script>