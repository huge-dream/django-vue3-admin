<template>
    <div style="width: 100%; height: 100%;">
      <div class="selected-show" v-if="props.modelValue && props.selectable">
        <el-text>已选择:</el-text>
        <el-tag v-if="props.multiple" v-for="item in data" closable @close="handleTagClose(item)">
          {{ item.toLocaleDateString('en-CA') }}
        </el-tag>
        <el-tag v-else closable @close="handleTagClose(data)">{{ data?.toLocaleDateString('en-CA') }}</el-tag>
        <el-button v-if="props.modelValue" size="small" type="text" @click="clear">清空</el-button>
      </div>
      <div class="controls">
        <div>
          今天：<el-text size="large">{{ today.toLocaleDateString('en-CA') }}</el-text>
        </div>
        <!-- <div class="current-month">
          <el-tag size="large" type="primary">
            {{ currentCalendarDate.getFullYear() }}年{{ currentCalendarDate.getMonth() + 1 }}月
          </el-tag>
        </div> -->
        <div class="control-button" v-if="!(!!props.range && props.range[0] && props.range[1]) && props.showPageTurn">
          <el-button-group size="small" type="default" v-if="props.pageTurn">
            <el-popover trigger="click" width="160px">
              <template #reference>
                <el-button type="text" size="small">节假日设置</el-button>
              </template>
              <el-switch v-model="showHoliday" active-text="显示节日" inactive-text="关闭节日" inline-prompt />
              <el-checkbox v-model="showLunarHoliday" label="农历节日" />
              <el-checkbox v-model="showJieQi" label="节气" />
              <el-checkbox v-model="showDetailedHoliday" label="更多节日" />
            </el-popover>
            <el-button icon="DArrowLeft" @click="turnToPreY">上年</el-button>
            <el-button icon="ArrowLeft" @click="turnToPreM">上月</el-button>
            <el-button @click="turnToToday">今天</el-button>
            <el-button icon="ArrowRight" @click="turnToNextM">下月</el-button>
            <el-button icon="DArrowRight" @click="turnToNextY">下年</el-button>
          </el-button-group>
        </div>
      </div>
      <el-divider style="margin: 4px;" />
      <div class="calender">
        <table style="width: 100%; border-collapse: collapse;">
          <thead>
            <tr>
              <th class="calender-header" v-for="item, ind in ['日', '一', '二', '三', '四', '五', '六']" :key="ind">
                {{ item }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="week in calendarList">
              <td class="calender-td" v-for="item in week">
                <div class="calender-cell" :data-date="item.date.toLocaleDateString('en-CA')" :class="{
                  'no-current-month': item.date.getMonth() !== currentCalendarDate.getMonth(),
                  'today': item.date.toDateString() === today.toDateString(),
                  'selected': item.selected,
                  'disabled': item.disabled,
                }" @mouseenter="onCalenderCellHover" @mouseleave="onCalenderCellUnhover"
                  @click="(e: MouseEvent) => item.disabled ? null : onCalenderCellClick(e)">
                  <div class="calender-cell-header calender-cell-line">
                    <span>{{ item.date.getDate() }}</span>
                    <span v-if="item.selected">
                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 1024 1024">
                        <path fill="currentColor"
                          d="M77.248 415.04a64 64 0 0 1 90.496 0l226.304 226.304L846.528 188.8a64 64 0 1 1 90.56 90.496l-543.04 543.04-316.8-316.8a64 64 0 0 1 0-90.496z">
                        </path>
                      </svg>
                    </span>
                  </div>
                  <div class="calender-cell-body calender-cell-line">
                    <slot name="cell-body" v-bind="item">
                    </slot>
                  </div>
                  <div class="calender-cell-footer calender-cell-line">
                    <span>{{ item.holiday || '&nbsp;' }}</span>
                    <el-text v-if="item.date.toDateString() === today.toDateString()" type="danger">今天</el-text>
                  </div>
                  <!-- {{ item }} -->
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div class="watermark" v-if="props.watermark" :style="watermarkPositionMap[props.watermarkPosition]">
          {{ (currentCalendarDate.toLocaleDateString('en-CA').split('-').slice(0, 2)).join('-') }}
        </div>
      </div>
    </div>
  </template>
  
  <script lang="ts" setup>
  import { useUi } from '@fast-crud/fast-crud';
  import { ref, defineProps, PropType, watch, computed, onMounted } from 'vue';
  import Holidays from 'date-holidays';
  import Lunar from 'lunar-javascript';
  const LUNAR = Lunar.Lunar; // 农历
  const SOLAR = Lunar.Solar; // 阳历
  
  const props = defineProps({
    modelValue: {},
    // 日期多选
    multiple: { type: Boolean, default: false },
    // 日期范围
    range: { type: Object as PropType<[Date, Date]> },
    // 可以翻页
    pageTurn: { type: Boolean, default: true },
    // 跨页选择
    crossPage: { type: Boolean, default: false },
    // 显示年月水印和水印位置
    watermark: { type: Boolean, default: true },
    watermarkPosition: { type: Object as PropType<PositionType>, default: 'bottom-right' },
    // 显示翻页控件
    showPageTurn: { type: Boolean, default: true },
    // 是否可选
    selectable: { type: Boolean, default: true },
    // 验证日期是否有效
    validDate: { type: Object as PropType<ValidDateFunc>, default: () => ((d: Date) => true) }
  });
  type ValidDateFunc = (d: Date) => boolean;
  type PositionType = 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' | 'center' | 'center-left' | 'center-right' | 'center-top';
  const today = new Date();
  const showHoliday = ref<boolean>(true); // 显示节日
  const showDetailedHoliday = ref<boolean>(false); // 显示详细的国际节日
  const showJieQi = ref<boolean>(true); // 显示节气
  const showLunarHoliday = ref<boolean>(true); // 显示农历节日
  const watermarkPositionMap: { [key: string]: any } = {
    'top-left': { top: '40px', left: 0, transformOrigin: '0 0' },
    'top-right': { top: '40px', right: 0, transformOrigin: '100% 0' },
    'bottom-left': { bottom: 0, left: 0, transformOrigin: '0 100%' },
    'bottom-right': { bottom: 0, right: 0, transformOrigin: '100% 100%' },
    'center': { top: '50%', left: '50%', transformOrigin: '50% 50%', transform: 'translate(-50%, -50%) scale(10)' },
    'center-left': { top: '50%', left: 0, transformOrigin: '0 50%' },
    'center-right': { top: '50%', right: 0, transformOrigin: '100% 50%' },
    'center-top': { top: 0, left: '50%', transformOrigin: '50% 0', transform: 'translate(-50%, 40px) scale(10)' },
    'center-bottom': { bottom: 0, left: '50%', transformOrigin: '50% 100%', transform: 'translate(-50%, 0) scale(10)' },
  };
  // 获取当月第一周的第一天（包括上个月）
  const calendarFirstDay = (current: Date = new Date()) => {
    let today = new Date(current); // 指定天
    let firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 1); // 月初天
    let weekOfFirstDay = firstDayOfMonth.getDay(); // 周几，0日
    if (weekOfFirstDay === 0) return new Date(firstDayOfMonth); // 是周日则直接返回
    let firstDayOfWeek = new Date(firstDayOfMonth);
    // 月初减去周几，不+1是因为从日历周日开始
    firstDayOfWeek.setDate(firstDayOfMonth.getDate() - weekOfFirstDay);
    return new Date(firstDayOfWeek);
  };
  // 获取当月最后一周的最后一天（包括下个月）
  const calendarLastDay = (current: Date = new Date()) => {
    let today = new Date(current); // 指定天
    let lastDayOfMonth = new Date(today.getFullYear(), today.getMonth() + 1, 1); // 月末天
    lastDayOfMonth.setDate(lastDayOfMonth.getDate() - 1);
    let weekOfFirstDay = lastDayOfMonth.getDay();
    if (weekOfFirstDay === 6) return new Date(lastDayOfMonth); // 是周六则直接返回
    let lastDayOfWeek = new Date(lastDayOfMonth);
    // 月末加剩下周几，要-1是因为日历到周六结束
    lastDayOfWeek.setDate(lastDayOfMonth.getDate() + (7 - weekOfFirstDay - 1));
    return new Date(lastDayOfWeek);
  };
  const generateDateList = (startDate: Date, endDate: Date): Date[] => { // 生成日期列表
    let dates = [];
    let s = new Date(startDate);
    let e = new Date(endDate);
    while (s <= e) {
      dates.push(new Date(s));
      s.setDate(s.getDate() + 1);
    }
    return dates;
  };
  // 日历当前页范围
  interface CalendarCell {
    date: Date;
    selected: boolean;
    disabled: boolean;
    currentMonth: boolean;
    holiday: string;
  };
  const currentCalendarDate = ref<Date>(new Date());
  const calendarList = computed(() => {
    let dates = (!!props.range && props.range[0] && props.range[1]) ?
      generateDateList(props.range[0], props.range[1]) :
      generateDateList(calendarFirstDay(currentCalendarDate.value), calendarLastDay(currentCalendarDate.value));
    let proce_dates: CalendarCell[] = dates.map((value) => {
      let solarDate = SOLAR.fromDate(value);
      let lunarDate = solarDate.getLunar();
      let solarHolidays: string[] = solarDate.getFestivals(); // 国历节日
      let lunarHolidays: string[] = lunarDate.getFestivals(); // 农历节日
      let jieQi: string = lunarDate.getJieQi(); // 节气
      // 农历节日、国际节日、节气三选一
      let holiday = showHoliday.value ? ((showLunarHoliday.value ? lunarHolidays[0] : '') || (showJieQi.value ? jieQi : '') ||
        (showDetailedHoliday.value ? solarHolidays[0] : yearHolidays.value[value.toLocaleDateString('en-CA')])) : ''; // yearHolidays国际的
      return {
        date: value,
        selected: props.multiple ?
          (data.value as Date[]).findIndex((v) => v.toLocaleDateString('en-CA') === value.toLocaleDateString('en-CA')) !== -1 :
          data.value?.toLocaleDateString('en-CA') === value.toLocaleDateString('en-CA'),
        disabled: !props.validDate(value),
        currentMonth: value.getMonth() === currentCalendarDate.value.getMonth(),
        // 农历节日、节气、法定日三选一
        holiday: holiday
      }
    });
    let res: CalendarCell[][] = [];
    for (let i = 0; i < 6; i++) res.push(proce_dates.slice(i * 7, (i + 1) * 7));
    return res;
  });
  // 控件
  const turnToPreM = () => currentCalendarDate.value = new Date(currentCalendarDate.value.getFullYear(), currentCalendarDate.value.getMonth() - 1, 1);
  const turnToNextM = () => currentCalendarDate.value = new Date(currentCalendarDate.value.getFullYear(), currentCalendarDate.value.getMonth() + 1, 1);
  const turnToPreY = () => currentCalendarDate.value = new Date(currentCalendarDate.value.getFullYear() - 1, currentCalendarDate.value.getMonth(), 1);
  const turnToNextY = () => currentCalendarDate.value = new Date(currentCalendarDate.value.getFullYear() + 1, currentCalendarDate.value.getMonth(), 1);
  const turnToToday = () => currentCalendarDate.value = new Date();
  // 如果禁止跨页则跨页时清空选择
  watch(
    () => currentCalendarDate.value,
    (v, ov) => props.crossPage ? {} :
      (v.toLocaleDateString('en-CA') === ov.toLocaleDateString('en-CA') ? {} : clear())
  );
  // 单元格事件
  const onCalenderCellHover = ({ target }: MouseEvent) => (target as HTMLElement).classList.add('onhover');
  const onCalenderCellUnhover = ({ target }: MouseEvent) => (target as HTMLElement).classList.remove('onhover');
  const onCalenderCellClick = (e: MouseEvent) => {
    if (!props.selectable) return;
    let strValue = (e.target as HTMLElement).dataset.date as string;
    if (strValue === undefined) return;
    let value = new Date(strValue);
    if (props.multiple) {
      let d = (data.value as Date[]).map((v) => v.toLocaleDateString('en-CA'));
      let ind = d.findIndex((v) => v === strValue);
      if (ind === -1) d.push(strValue);
      else d.splice(ind, 1);
      onDataChange(d);
    }
    // 这里阻止了点击取消选中，需要通过tag的x来取消
    else (data.value?.toLocaleDateString('en-CA') === strValue ? {} : onDataChange(value));
  };
  // 选择回显
  const handleTagClose = (d: Date) => {
    let strValue = d.toLocaleDateString('en-CA');
    if (props.multiple) {
      let d = (data.value as Date[]).map((v) => v.toLocaleDateString('en-CA'));
      d.splice(d.findIndex((v) => v === strValue), 1);
      onDataChange(d);
    }
    else onDataChange(null);
  };
  // 节假日
  const holidays = new Holidays('CN');
  const yearHolidays = computed(() => {
    let h = holidays.getHolidays(currentCalendarDate.value.getFullYear());
    let proce_h: { [key: string]: string } = {};
    let _h: string[] = [];
    for (let i of h) {
      let d = i.date.split(' ')[0];
      let hn = i.name.split(' ')[0];
      if (_h.includes(hn)) continue;
      proce_h[d] = hn;
      _h.push(hn);
    }
    return proce_h
  });
  
  // fs-crud部分
  const data = ref<any>();
  const emit = defineEmits(['update:modelValue', 'onSave', 'onClose', 'onClosed']);
  watch(
    () => props.modelValue,
    (val) => {
      if (val === undefined) data.value = props.multiple ? [] : null;
      else data.value = props.multiple ? (val as Date[]).map((v: Date) => new Date(v)) : val;
    },
    { immediate: true }
  );
  const { ui } = useUi();
  const formValidator = ui.formItem.injectFormItemContext();
  const onDataChange = (value: any) => {
    emit('update:modelValue', value);
    formValidator.onChange();
    formValidator.onBlur();
  };
  const reset = () => { // 重置日历
    currentCalendarDate.value = new Date();
    onDataChange(props.multiple ? [] : null);
  };
  const clear = () => onDataChange(props.multiple ? [] : null); // 清空数据
  defineExpose({
    data,
    onDataChange,
    reset,
    clear,
    showHoliday,
    showDetailedHoliday,
    showJieQi,
    showLunarHoliday
  });
  
  
  </script>
  
  <style lang="scss" scoped>
  .selected-show {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .controls {
    width: 100%;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  
  .calender {
    position: relative;
    width: 100%;
    overflow-x: auto;
    overflow-y: hidden;
    scrollbar-width: thin;
  
    .watermark {
      position: absolute;
      font-size: 16px;
      transform: scale(10);
      color: #aaa;
      opacity: 0.1;
      pointer-events: none;
    }
  
    table {
      position: relative;
    }
  
    .calender-header {
      padding: 16px 0;
    }
  
    .calender-td {
      border: 1px solid #eee;
      width: calc(100% / 7);
    }
  
    .calender-cell {
      min-height: 96px;
      min-width: 100px;
      box-sizing: border-box;
      padding: 12px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      cursor: pointer;
  
      &.today {
        color: var(--el-color-warning) !important;
        background-color: var(--el-color-warning-light-9) !important;
      }
  
      &.onhover {
        color: var(--el-color-primary);
        background-color: var(--el-color-primary-light-9);
      }
  
      &.disabled {
        cursor: not-allowed;
        color: #bbb;
        background: none;
      }
  
      &.no-current-month {
        color: #bbb;
      }
  
      &.selected {
        color: var(--el-color-primary);
        background-color: var(--el-color-primary-light-9);
      }
  
      .calender-cell-line {
        min-height: 0px;
  
        &.calender-cell-header {
          display: flex;
          gap: 4px;
          align-items: center;
          pointer-events: none;
        }
  
        &.calender-cell-body {
          display: flex;
          gap: 4px;
          align-items: center;
        }
  
        &.calender-cell-footer {
          display: flex;
          justify-content: space-between;
          pointer-events: none;
        }
      }
    }
  }
  </style>
  