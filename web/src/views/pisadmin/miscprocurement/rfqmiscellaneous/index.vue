<template>
  <fs-page>
    <fs-crud ref="crudRef" v-bind="crudBinding" />

    <el-dialog v-model="dialog.visible" :title="dialogTitle" width="1200px">
      <div class="dialog-body">
        <div class="status-bar">
          <span>状态：</span>
          <el-tag :type="statusTagType(form.status)">{{ statusLabel(form.status) }}</el-tag>
        </div>

        <el-tabs v-model="activeTab" type="card" class="tabs-fill">
        <el-tab-pane label="基础信息" name="base">
          <el-form :model="form" :disabled="isViewMode" label-width="120px" class="grid-form">
             <el-form-item label="交易厂区">
                  <el-select
                    v-model="form.plant"
                    placeholder="选择交易厂区"
                    :loading="companyLoading"
                    filterable
                    clearable
                    @change="handlePlantChange"
                  >
                    <el-option v-for="c in companyOptions" :key="c.value" :label="c.label" :value="c.value" />
                  </el-select>
                </el-form-item>
            <el-form-item label="询价单号">
              <el-input v-model="form.inquiry_no" placeholder="保存后自动生成" disabled />
            </el-form-item>
            <el-form-item label="询价单名称" required>
              <el-input v-model="form.title" />
            </el-form-item>
            <el-form-item label="询价模版" required>
              <el-select
                v-model="form.template"
                placeholder="选择模版"
                :loading="templateLoading"
                filterable
              >
                <el-option v-for="tpl in templateOptions" :key="tpl.value" :label="tpl.label" :value="tpl.value" />
              </el-select>
            </el-form-item>
            <el-form-item label="采购件料号" required>
              <el-select
                v-model="form.part_no"
                placeholder="选择采购件料号"
                :loading="partLoading"
                filterable
                clearable
                @change="handlePartChange"
              >
                <el-option
                  v-for="p in partOptions"
                  :key="p.value"
                  :label="p.label"
                  :value="p.value"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="采购件名称">
              <el-input v-model="form.part_name" />
            </el-form-item>           
            <el-form-item label="产品类别" required>
              <el-select v-model="form.product_category" placeholder="根据模版自动带出" disabled>
                <el-option v-for="c in categoryDict" :key="c.value" :label="c.label" :value="c.value" />
              </el-select>
            </el-form-item>
            <el-form-item label="采购方式" required>
              <el-select v-model="form.buying_method" placeholder="采购方式" clearable>
                <el-option :value="1" label="询价" />
                <el-option :value="2" label="招标" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="isInquiryBuyingMethod" label="报价截止时" required>
              <div class="quote-deadline-input">
                <el-date-picker
                  v-model="quoteDeadlineDate"
                  type="date"
                  value-format="YYYY-MM-DD"
                  placeholder="选择日期"
                  :disabled-date="isQuoteDeadlineDateDisabled"
                  style="max-width: 100%"
                />
                <el-select v-model="quoteDeadlineHour" placeholder="小时" :disabled="!quoteDeadlineDate" style="max-width: 120px">
                  <el-option v-for="hour in quoteDeadlineHourOptions" :key="hour" :label="`${hour}:00`" :value="hour" />
                </el-select>
              </div>
            </el-form-item>
            <el-form-item v-if="!isInquiryBuyingMethod" label="投标开始时间" required>
              <div class="quote-deadline-input">
                <el-date-picker
                  v-model="bidStartTimeDate"
                  type="date"
                  value-format="YYYY-MM-DD"
                  placeholder="选择日期"
                  :disabled-date="isQuoteDeadlineDateDisabled"
                  style="max-width: 100%"
                />
                <el-select v-model="bidStartTimeHour" placeholder="小时" :disabled="!bidStartTimeDate" style="max-width: 120px">
                  <el-option v-for="hour in quoteDeadlineHourOptions" :key="hour" :label="`${hour}:00`" :value="hour" />
                </el-select>
              </div>
            </el-form-item>
            <el-form-item v-if="!isInquiryBuyingMethod" label="投标截止时间" required>
              <div class="quote-deadline-input">
                <el-date-picker
                v-model="bidEndTimeDate"
                type="date"
                  value-format="YYYY-MM-DD"
                  placeholder="选择日期"
                  :disabled-date="isQuoteDeadlineDateDisabled"
                  style="width: 100%"
                />
                <el-select v-model="bidEndTimeHour" placeholder="小时" :disabled="!bidEndTimeDate" style="width: 120px">
                  <el-option v-for="hour in quoteDeadlineHourOptions" :key="hour" :label="`${hour}:00`" :value="hour" />
                </el-select>
              </div>
            </el-form-item>
            <el-form-item label="是否成本结构">
              <el-switch
                v-model="form.is_bom"
                :active-value="1"
                :inactive-value="0"
                active-text="是"
                inactive-text="否"
                disabled
              />
            </el-form-item>
            <el-form-item label="采购部门">
              <el-input v-model="form.purchase_dept" placeholder="当前登录用户所属部门" disabled />
            </el-form-item>
            <el-form-item label="采购人员" required>
              <el-input v-model="form.buyer" />
            </el-form-item>
            <el-form-item label="采购数量">
              <el-input-number v-model="form.purchase_qty" :min="1" :precision="2" controls-position="right" />
            </el-form-item>            
            <el-form-item label="交易币别">
              <el-select
                v-model="form.currency"
                placeholder="根据厂区自动带出"
                :loading="currencyLoading"
                filterable
                clearable
              >
                <el-option
                  v-for="c in currencyOptions"
                  :key="c.value"
                  :label="c.label"
                  :value="c.value"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="目标价格">
              <el-input-number v-model="form.target_price" :min="0" :precision="2" controls-position="right" />
            </el-form-item>
            <el-form-item label="交货周期(天)">
              <el-input-number v-model="form.lead_time_days" :min="0" :precision="0" controls-position="right" />
            </el-form-item>
            <el-form-item label="付款方式">
              <el-select v-model="form.payment_method" placeholder="选择付款方式">
                <el-option v-for="p in paymentMethods" :key="p.value" :label="p.label" :value="p.value" />
              </el-select>
            </el-form-item>
            <el-form-item label="备注" class="span3">
              <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="补充备注" />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="成本结构" name="cost">
          <div class="cost-header mb8">
            <span>根据模板加载成本结构，字段随模板变化</span>
            <el-button v-if="!isViewMode" size="small" @click="loadCostItemsFromTemplate(currentTemplate, true)">重新加载模板</el-button>
          </div>
          <div class="cost-groups">
            <div v-for="section in primarySections" :key="section" class="cost-group">
              <div class="cost-group-header">
                <div class="cost-section-title">{{ section }}</div>
                <el-button
                  v-if="!isViewMode && sectionAddConfig[section]"
                  size="small"
                  type="primary"
                  @click="addCostRow(section)"
                >新增一行</el-button>
              </div>
              <el-table :data="(groupedCostRows[section] || [])" border size="small" class="mb12">
                <el-table-column
                  v-for="col in sectionColumns[section] || []"
                  :key="col.key"
                  :prop="col.key"
                  :label="col.label"
                >
                  <template #default="{ row }">
                    <el-select
                      v-if="section === '材料成本' && col.key === 'material'"
                      v-model="row.values[col.key]"
                      placeholder="选择材质"
                      :loading="materialLoading"
                      :disabled="isCostFieldReadonly(section, col.key)"
                      filterable
                      clearable
                      @change="(val: string) => handleMaterialSelect(row, val)"
                    >
                      <el-option
                        v-for="m in materialOptions"
                        :key="m.value"
                        :label="m.label"
                        :value="m.value"
                      />
                    </el-select>
                    <el-select
                      v-else-if="section === '加工成本' && col.key === 'process_station'"
                      v-model="row.values[col.key]"
                      placeholder="选择加工工站"
                      :loading="stationLoading"
                      :disabled="isCostFieldReadonly(section, col.key)"
                      filterable
                      clearable
                      @change="(val: string) => handleStationSelect(row, val)"
                    >
                      <el-option
                        v-for="s in stationOptions"
                        :key="s.value"
                        :label="s.label"
                        :value="s.value"
                      />
                    </el-select>
                    <el-select
                      v-else-if="section === '加工成本' && processUnitKeys.includes(col.key)"
                      v-model="row.values[col.key]"
                      placeholder="选择单位"
                      :loading="unitLoading"
                      :disabled="isCostFieldReadonly(section, col.key)"
                      filterable
                      clearable
                    >
                      <el-option v-for="u in unitOptions" :key="u.value" :label="u.label" :value="u.value" />
                    </el-select>
                    <el-input
                      v-else-if="section === '加工成本' && processRateKeys.includes(col.key)"
                      v-model="row.values[col.key]"
                      :placeholder="col.label"
                      disabled
                    />
                    <el-input
                      v-else-if="section === '加工成本' && processFeeKeys.includes(col.key)"
                      v-model="row.values[col.key]"
                      :placeholder="col.label"
                      disabled
                    />
                    <el-input
                      v-else-if="section === '加工成本'"
                      v-model="row.values[col.key]"
                      :placeholder="col.label"
                      :disabled="isCostFieldReadonly(section, col.key)"
                      @input="() => updateProcessCalc(row)"
                    />
                    <el-input
                      v-else-if="section === '材料成本' && col.key === 'specificgravity'"
                      v-model="row.values[col.key]"
                      :placeholder="col.label"
                      :disabled="isCostFieldReadonly(section, col.key)"
                      @input="() => updateMaterialCalc(row)"
                    />
                    <el-input
                      v-else-if="section === '材料成本' && weightKeys.includes(col.key)"
                      v-model="row.values[col.key]"
                      :placeholder="col.label"
                      disabled
                    />
                    <el-input
                      v-else-if="section === '材料成本' && materialFeeKeys.includes(col.key)"
                      v-model="row.values[col.key]"
                      :placeholder="col.label"
                      disabled
                    />
                    <el-input
                      v-else-if="section === '材料成本'"
                      v-model="row.values[col.key]"
                      :placeholder="col.label"
                      :disabled="isCostFieldReadonly(section, col.key)"
                      @input="() => updateMaterialCalc(row)"
                    />
                    <el-input
                      v-else
                      v-model="row.values[col.key]"
                      :placeholder="col.label"
                      :disabled="isCostFieldReadonly(section, col.key)"
                    />
                  </template>
                </el-table-column>
                <el-table-column v-if="!isViewMode && sectionAddConfig[section]" label="操作" width="100">
                  <template #default="{ row }">
                    <el-button link type="danger" size="small" @click="removeCostRow(row)">移除</el-button>
                  </template>
                </el-table-column>
              </el-table>
              <el-empty v-if="!(groupedCostRows[section] || []).length" description="暂无数据" />
            </div>

            <div class="cost-row-pair">
              <div v-for="section in profitTaxSections" :key="section" class="cost-group">
                <div class="cost-group-header">
                  <div class="cost-section-title">{{ section }}</div>
                </div>
                <el-table :data="(groupedCostRows[section] || [])" border size="small" class="mb12">
                  <el-table-column
                    v-for="col in sectionColumns[section] || []"
                    :key="col.key"
                    :prop="col.key"
                    :label="col.label"
                  >
                    <template #default="{ row }">
                      <el-input
                        v-model="row.values[col.key]"
                        :placeholder="col.label"
                        :disabled="isCostFieldReadonly(section, col.key)"
                      />
                    </template>
                  </el-table-column>
                </el-table>
                <el-empty v-if="!(groupedCostRows[section] || []).length" description="暂无数据" />
              </div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="供应商名单" name="vendors">
          <div class="table-actions mb8">
            <el-button v-if="!isViewMode" type="primary" size="small" @click="addVendorRow">新增一行</el-button>
          </div>
          <el-table :data="form.vendors" border size="small" class="mb8">
            <el-table-column prop="name" label="供应商">
              <template #default="{ row }">
                <el-select
                  v-model="row.name"
                  placeholder="选择供应商"
                  :loading="supplierLoading"
                  :disabled="isViewMode"
                  filterable
                  clearable
                  @change="(val: string) => handleVendorSelect(row, val)"
                >
                  <el-option
                    v-for="s in supplierOptionsForVendorRow(row)"
                    :key="s.value"
                    :label="s.label"
                    :value="s.value"
                  />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column prop="contact" label="联系人">
              <template #default="{ row }">
                <el-input v-model="row.contact" placeholder="联系人" :disabled="isViewMode" />
              </template>
            </el-table-column>
            <el-table-column prop="email" label="邮箱">
              <template #default="{ row }">
                <el-input v-model="row.email" placeholder="邮箱" :disabled="isViewMode" />
              </template>
            </el-table-column>
            <el-table-column v-if="!isViewMode" label="操作" width="120">
              <template #default="{ row }">
                <el-button link type="danger" size="small" @click="removeVendor(row)">移除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="附件" name="attachments">
          <div class="attach-grid">
            <div class="attach-block">
              <div class="attach-title">产品图纸</div>
              <el-upload
                action="#"
                :auto-upload="false"
                multiple
                list-type="text"
                :disabled="isViewMode"
                :file-list="form.attachments.drawing"
                :on-change="(file, list) => onAttachmentChange('drawing', list)"
                :on-remove="(file, list) => onAttachmentChange('drawing', list)"
              >
                <el-button v-if="!isViewMode" size="small" type="primary">上传图纸</el-button>
              </el-upload>
            </div>
            <div class="attach-block">
              <div class="attach-title">招标文件</div>
              <el-upload
                action="#"
                :auto-upload="false"
                multiple
                list-type="text"
                :disabled="isViewMode"
                :file-list="form.attachments.tender"
                :on-change="(file, list) => onAttachmentChange('tender', list)"
                :on-remove="(file, list) => onAttachmentChange('tender', list)"
              >
                <el-button v-if="!isViewMode" size="small" type="primary">上传文件</el-button>
              </el-upload>
            </div>
            <div class="attach-block">
              <div class="attach-title">其它文件</div>
              <el-upload
                action="#"
                :auto-upload="false"
                multiple
                list-type="text"
                :disabled="isViewMode"
                :file-list="form.attachments.other"
                :on-change="(file, list) => onAttachmentChange('other', list)"
                :on-remove="(file, list) => onAttachmentChange('other', list)"
              >
                <el-button v-if="!isViewMode" size="small" type="primary">上传文件</el-button>
              </el-upload>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
      </div>

      <template #footer>
        <el-button @click="dialog.visible = false">{{ isViewMode ? '关闭' : '取消' }}</el-button>
        <el-button v-if="!isViewMode" type="primary" @click="saveForm">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="comparisonDialog.visible" :title="comparisonDialog.title" width="1200px">
      <div class="compare-body" v-loading="comparisonDialog.loading">
        <div class="compare-info">
          <div class="info-item"><span class="label">询价单号</span><span class="value">{{ displayTextEmpty(comparisonDialog.baseInfo.code) }}</span></div>
          <div class="info-item"><span class="label">采购件料号</span><span class="value">{{ displayTextEmpty(comparisonDialog.baseInfo.partNo) }}</span></div>
          <div class="info-item"><span class="label">采购件名称</span><span class="value">{{ displayTextEmpty(comparisonDialog.baseInfo.partName) }}</span></div>
          <div class="info-item"><span class="label">目标价格</span><span class="value">{{ displayNumericEmpty(comparisonDialog.baseInfo.targetPrice) }}</span></div>
          <div class="info-item"><span class="label">交易币别</span><span class="value">{{ displayTextEmpty(comparisonDialog.baseInfo.currency) }}</span></div>
          <div class="info-item"><span class="label">税率</span><span class="value">{{ displayPercentRate(comparisonDialog.baseInfo.taxRate) }}</span></div>
          <div class="info-item"><span class="label">当前成交价</span><span class="value">{{ displayNumericEmpty(comparisonDialog.baseInfo.dealPrice) }}</span></div>
          <div class="info-item"><span class="label">制程最低价</span><span class="value">{{ displayNumericEmpty(comparisonDialog.baseInfo.lowestProcessPrice) }}</span></div>
        </div>

        <el-table
          :key="compareTableRenderKey"
          ref="compareTableRef"
          :data="comparisonDialog.rows"
          border
          size="small"
          class="compare-table"
          :row-key="comparisonRowKeyFn"
          :row-class-name="comparisonRowClassName"
          @expand-change="handleComparisonExpandChange"
        >
          <el-table-column type="expand" width="1" class-name="hidden-expand" header-class-name="hidden-expand">
            <template #default="{ row }">
              <div class="compare-detail">
                <template v-if="row.detailGroups && row.detailGroups.length">
                  <div v-for="grp in row.detailGroups" :key="grp.title" class="compare-detail-group">
                    <div class="compare-detail-group-title">{{ grp.title }}</div>
                    <el-table :data="grp.lines" size="small" border class="compare-detail-table">
                      <el-table-column label="明细" prop="label" min-width="140" />
                      <el-table-column
                        v-for="(sup, supIdx) in comparisonDialog.suppliers"
                        :key="`${grp.title}-${sup.name}`"
                        :prop="`values.${sup.name}`"
                        min-width="120"
                      >
                        <template #header>
                          <span class="supplier-header-link" title="预览该供应商报价单" @click.stop="openQuotationPreview(supIdx)">
                            {{ sup.name }}
                          </span>
                        </template>
                        <template #default="{ row: line }">
                          <span :class="['compare-value', line.min === line.values[sup.name] ? 'is-min' : '']">
                            {{ formatMetricDetailCell(line.values[sup.name], line.label, line.isText) }}
                          </span>
                        </template>
                      </el-table-column>
                      <el-table-column prop="avg" label="平均价" width="100">
                        <template #default="{ row: line }">{{ formatCompareAvg(line.avg, row.key) }}</template>
                      </el-table-column>
                      <el-table-column prop="min" label="制程最低价" width="110">
                        <template #default="{ row: line }">{{ formatCompareMin(line.min, row.key) }}</template>
                      </el-table-column>
                    </el-table>
                  </div>
                </template>
                <el-table
                  v-else-if="row.details && row.details.length"
                  :data="row.details"
                  size="small"
                  border
                  class="compare-detail-table"
                >
                  <el-table-column :label="detailHeaderLabel(row)" prop="label" min-width="140" />
                  <el-table-column
                    v-for="(sup, supIdx) in comparisonDialog.suppliers"
                    :key="sup.name"
                    :prop="`values.${sup.name}`"
                    min-width="140"
                  >
                    <template #header>
                      <span class="supplier-header-link" title="预览该供应商报价单" @click.stop="openQuotationPreview(supIdx)">
                        {{ sup.name }}
                      </span>
                    </template>
                    <template #default="{ row: detail }">
                      <span :class="['compare-value', detail.min === detail.values[sup.name] ? 'is-min' : '']">
                        {{ formatMetricDetailCell(detail.values[sup.name], detail.label, detail.isText) }}
                      </span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="avg" label="平均价" width="120">
                    <template #default="{ row: detail }">{{ formatCompareAvg(detail.avg, row.key) }}</template>
                  </el-table-column>
                  <el-table-column prop="min" label="制程最低价" width="120">
                    <template #default="{ row: detail }">{{ formatCompareMin(detail.min, row.key) }}</template>
                  </el-table-column>
                </el-table>
                <div v-else class="no-detail">暂无明细</div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="label" label="成本结构" fixed="left" min-width="160">
            <template #default="{ row }">
              <span
                v-if="(row.details && row.details.length) || (row.detailGroups && row.detailGroups.length)"
                class="expand-toggle"
                @click.stop="toggleCompareExpand(row)"
              >
                {{ expandedRowKeys.includes(comparisonRowKeyFn(row)) ? '－' : '＋' }}
              </span>
              <span>{{ row.label }}</span>
            </template>
          </el-table-column>
          <el-table-column
            v-for="(sup, supIdx) in comparisonDialog.suppliers"
            :key="sup.name"
            :prop="`values.${sup.name}`"
            min-width="140"
          >
            <template #header>
              <span class="supplier-header-link" title="预览该供应商报价单" @click.stop="openQuotationPreview(supIdx)">
                {{ sup.name }}
              </span>
            </template>
            <template #default="{ row }">
              <template v-if="row.key === 'bargain'">
                <el-input v-model="row.values[sup.name]" size="small" placeholder="请输入议价价" />
              </template>
              <template v-else-if="row.key === 'award'">
                <el-switch
                  :model-value="row.values[sup.name] === '是'"
                  @update:model-value="(val: boolean) => toggleComparisonAward(row, sup.name, val)"
                  active-text="是"
                  inactive-text="否"
                />
              </template>
              <template v-else>
                <span :class="['compare-value', row.min === row.values[sup.name] ? 'is-min' : '']">
                  {{ formatComparisonMainCell(row, row.values[sup.name]) }}
                </span>
              </template>
            </template>
          </el-table-column>
          <el-table-column prop="avg" label="平均价" width="120">
            <template #default="{ row }">{{ row.key === 'bargain' ? '-' : formatCompareAvg(row.avg, row.key) }}</template>
          </el-table-column>
          <el-table-column prop="min" label="制程最低价" width="120">
            <template #default="{ row }">{{ row.key === 'bargain' ? '-' : formatCompareMin(row.min, row.key) }}</template>
          </el-table-column>
        </el-table>
      </div>
      <template #footer>
        <el-button @click="onSaveComparisonDraft" :loading="comparisonDialog.loading" :disabled="![4, 5, 6].includes(comparisonInquiryStatus)">暂存</el-button>
        <el-button
          type="success"
          @click="onConfirmComparison"
          :loading="comparisonDialog.loading"
          :disabled="![4, 5, 6].includes(comparisonInquiryStatus)"
        >
          确认比价
        </el-button>
        <el-button
          type="primary"
          @click="onSubmitComparisonReview"
          :loading="comparisonDialog.loading"
          :disabled="comparisonInquiryStatus !== 7"
        >
          提交核价
        </el-button>
        <el-button @click="comparisonDialog.visible = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="quotationPreview.visible"
      :title="quotationPreview.title"
      width="960px"
      top="5vh"
      append-to-body
      destroy-on-close
      class="quotation-preview-dialog"
    >
      <div v-loading="quotationPreview.loading" class="quote-preview-body">
        <template v-if="quotationPreview.quote">
          <div class="quote-preview-section">
            <div class="quote-preview-section-title">基本信息</div>
            <el-descriptions :column="3" border size="small">
              <el-descriptions-item label="报价单号">{{ displayTextEmpty(quotationPreview.quote.quotation_no) }}</el-descriptions-item>
              <el-descriptions-item label="供应商">{{ displayTextEmpty(quotationPreview.quote.supplier_name) }}</el-descriptions-item>
              <el-descriptions-item label="供应商代码">{{ displayTextEmpty(quotationPreview.quote.supplier_code) }}</el-descriptions-item>
              <el-descriptions-item label="品名">{{ displayTextEmpty(quotationPreviewRfqItem?.product_name) }}</el-descriptions-item>
              <el-descriptions-item label="料号">{{ displayTextEmpty(quotationPreviewRfqItem?.part_id) }}</el-descriptions-item>
              <el-descriptions-item label="币别">{{ quotationPreviewCurrency }}</el-descriptions-item>
              <el-descriptions-item label="税费">{{ quotationPreviewTaxDisplay }}</el-descriptions-item>
              <!-- <el-descriptions-item label="报价截止">
                {{ quotationPreview.quote.quote_deadline || quotationPreview.quote.quoteDeadline || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="状态">{{ quotationPreviewStatusLabel }}</el-descriptions-item> -->
            </el-descriptions>
          </div>

          <div class="quote-preview-section">
            <div class="quote-preview-section-title">① 材料成本</div>
            <el-table :data="quotationPreview.quote.material_costs || []" border size="small" empty-text="暂无">
              <el-table-column prop="material_spec" label="材料规格" min-width="120" show-overflow-tooltip>
                <template #default="{ row }">{{ displayTextEmpty(row.material_spec) }}</template>
              </el-table-column>
              <el-table-column prop="weight" label="重量" width="90">
                <template #default="{ row }">{{ displayNumericEmpty(row.weight) }}</template>
              </el-table-column>
              <el-table-column prop="qty" label="用量" width="90">
                <template #default="{ row }">{{ displayNumericEmpty(row.qty) }}</template>
              </el-table-column>
              <el-table-column prop="unit_price" label="材料单价" width="100">
                <template #default="{ row }">{{ displayNumericEmpty(row.unit_price) }}</template>
              </el-table-column>
              <el-table-column prop="material_cost" label="材料费用" width="100">
                <template #default="{ row }">{{ displayNumericEmpty(row.material_cost) }}</template>
              </el-table-column>
              <el-table-column prop="remark" label="备注" min-width="100" show-overflow-tooltip>
                <template #default="{ row }">{{ displayTextEmpty(row.remark) }}</template>
              </el-table-column>
            </el-table>
          </div>

          <div class="quote-preview-section">
            <div class="quote-preview-section-title">② 加工成本</div>
            <el-table :data="quotationPreview.quote.process_costs || []" border size="small" empty-text="暂无">
              <el-table-column prop="process_station" label="加工(工站)" min-width="120" show-overflow-tooltip>
                <template #default="{ row }">{{ displayTextEmpty(row.process_station) }}</template>
              </el-table-column>
              <el-table-column prop="process_qty" label="加工数量" width="100">
                <template #default="{ row }">{{ displayNumericEmpty(row.process_qty) }}</template>
              </el-table-column>
              <el-table-column prop="unit_rate" label="加工单价" width="100">
                <template #default="{ row }">{{ displayNumericEmpty(row.unit_rate) }}</template>
              </el-table-column>
              <el-table-column prop="unit" label="单位" width="80">
                <template #default="{ row }">{{ displayTextEmpty(row.unit) }}</template>
              </el-table-column>
              <el-table-column prop="process_price" label="工站加工费" width="110">
                <template #default="{ row }">{{ displayNumericEmpty(row.process_price) }}</template>
              </el-table-column>
              <el-table-column prop="remark" label="备注" min-width="100" show-overflow-tooltip>
                <template #default="{ row }">{{ displayTextEmpty(row.remark) }}</template>
              </el-table-column>
            </el-table>
          </div>

          <div class="quote-preview-section">
            <div class="quote-preview-section-title">③ 其它费用</div>
            <el-table :data="quotationPreview.quote.other_costs || []" border size="small" empty-text="暂无">
              <el-table-column prop="packaging_cost" label="包装费" width="100">
                <template #default="{ row }">{{ displayNumericEmpty(row.packaging_cost) }}</template>
              </el-table-column>
              <el-table-column prop="transportation_cost" label="运输费" width="100">
                <template #default="{ row }">{{ displayNumericEmpty(row.transportation_cost) }}</template>
              </el-table-column>
            </el-table>
          </div>

          <div class="quote-preview-section">
            <div class="quote-preview-section-title">④ 利润</div>
            <el-table :data="quotationPreview.quote.profit_costs || []" border size="small" empty-text="暂无">
              <el-table-column prop="profit_rate" label="利润率" width="100">
                <template #default="{ row }">{{ displayPercentRate(row.profit_rate) }}</template>
              </el-table-column>
            </el-table>
          </div>

          <div class="quote-preview-section">
            <div class="quote-preview-section-title">⑤ 税金</div>
            <el-table :data="quotationPreviewTaxTableRows" border size="small">
              <el-table-column prop="tax_rate" label="税率" width="100">
                <template #default="{ row }">{{ displayPercentRate(row.tax_rate) }}</template>
              </el-table-column>
            </el-table>
          </div>
          
          <div class="quote-preview-section quote-preview-total">
            <div class="quote-preview-section-title">总价（含税）</div>
            <div class="quote-preview-total-value">{{ quotationPreviewTotalPrice }}</div>
          </div>
        </template>
        <div v-else class="no-detail">暂无报价数据</div>
      </div>
      <template #footer>
        <el-button type="primary" @click="quotationPreview.visible = false">关闭</el-button>
      </template>
    </el-dialog>
  </fs-page>
</template>

<script setup lang="ts" name="InquiryManagement">
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue'
import { useCrud, useExpose } from '@fast-crud/fast-crud'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getList as getQuotationList,
  getDetail as getQuotationDetail,
  update as updateQuotation
} from '../../../pissupplier/quotation/api'
import {
  createCrudOptions,
  normalizeDict,
  formatCostTemplateVersion,
  formatRfqApiErrorMessage,
  displayNumericEmpty,
  displayTextEmpty,
  displayPercentRate,
  buildMaterialComparisonMetricsFromTemplateFields,
  buildProcessComparisonMetricsFromTemplateFields,
  type ComparisonDetailMetric
} from './crud'
import * as api from './api'
import * as costTemplateApi from '../cost_template/api'
import { GetCompanies, GetList as GetCurrencies } from '../../basicinfo/currency/api'
import { GetList as GetParts } from '../misc_parts/api'
import { GetList as GetMaterials } from '../misc_materials/api'
import { GetList as GetSuppliers } from '../../basicinfo/supplier/api'
import { GetList as GetStations } from '../misc_stations/api'
import { GetList as GetUnits } from '../../basicinfo/unit/api'
import { useUserInfo } from '/@/stores/userInfo'

const crudRef = ref()
const crudBinding = ref()
const { crudExpose } = useExpose({ crudRef, crudBinding })

/** 列表勾选的询价单行，供后续「多询价单比价」等功能使用 */
const selectedInquiryRows = ref<any[]>([])

const categoryDict = [
  { value: 'tooling', label: '模治具' },
  { value: 'stamping', label: '冲压' },
  { value: 'injection', label: '注塑' },
  { value: 'equipment', label: '设备' },
  { value: 'plastic', label: '塑胶件' },
  { value: 'default', label: '通用' }
]

const statusDict = [
  { value: 1, label: '开立' },
  { value: 2, label: '确认' },
  { value: 3, label: '发布' },
  { value: 4, label: '报价中' },
  { value: 5, label: '报价结束' },
  { value: 6, label: '比议价中' },
  { value: 7, label: '价格审核' },
  { value: 8, label: '核价通过(结束)' },
  { value: 9, label: '落标(结束)' },
  { value: 0, label: '作废' }
]

const STATUS_OPEN = 1
const STATUS_CONFIRMED = 2
const STATUS_PUBLISHED = 3

const paymentMethods = [
  { value: 1, label: '月结30天' },
  { value: 2, label: '月结60天' },
  { value: 3, label: '不到付款' },
  { value: 4, label: '预付30%' },
  { value: 5, label: '预付50%' },
  { value: 6, label: '余款至生产' },
  { value: 7, label: '价格审核' },
  { value: 8, label: '价格结算(运费)' },
  { value: 9, label: '新建(结束)' }
]
const companyOptions = ref<{ value: string; label: string }[]>([])
const companyLoading = ref(false)
const currencyOptions = ref<{ value: string; label: string }[]>([])
const currencyLoading = ref(false)
const partOptions = ref<{ value: string; label: string; name?: string; unit?: string }[]>([])
const partLoading = ref(false)
const materialOptions = ref<{ value: string; label: string; density?: number; price?: number }[]>([])
const materialLoading = ref(false)
const supplierOptions = ref<{
  value: string
  label: string
  supplier_code?: string
  supplier_name?: string
  contact?: string
  email?: string
}[]>([])
const supplierLoading = ref(false)
const stationOptions = ref<{ value: string; label: string; rate?: number; unit?: string }[]>([])
const stationLoading = ref(false)
const unitOptions = ref<{ value: string; label: string; name?: string }[]>([])
const unitLoading = ref(false)
const costEnabledSections = ['材料成本', '加工成本', '其它成本', '利润', '税金']
const costDisabledSections = ['产品明细', '利润', '税金']
const profitTaxNames = ['利润', '税金']
const priceKeys = ['unitPrice', 'unitprice', 'price', 'unit_price']
const materialCalcKeys = ['length', 'width', 'height', 'specificgravity', 'unitPrice', 'unitprice', 'qty', 'quantity', 'num', 'count']
const weightKeys = ['weight', '重量']
const materialFeeKeys = ['material_fee', 'materialFee', 'material_cost', 'materialCost', 'material_amount', 'materialAmount', '材料费用']
const processUnitKeys = ['unit', 'process_unit', '单位']
const processRateKeys = ['unitrate', 'rate', 'process_rate', 'fee_rate']
const processQtyKeys = ['process_qty', 'processqty', 'qty', 'quantity', 'num', 'count']
const processFeeKeys = ['processprice', 'process_cost', '加工费', 'fee']
const taxRateKeys = ['taxRate', 'tax_rate', 'tax', 'taxrate', 'tax_ratio', 'taxratio', 'rate', '税率']
const supplierFactoryKeys = ['factory', 'plant', 'company_code', 'company', 'factory_code', 'factorycode', 'plant_code']
const supplierBehaviorCodeMap: Record<string, number> = {
  prefill_locked: 1,
  prefill_editable: 2,
  hidden_required: 3,
  hidden_optional: 4,
  required: 5,
  optional: 6
}
const attachmentTypeCodeMap = {
  drawing: 1,
  tender: 2,
  other: 3
} as const
const attachmentTypeKeyMap: Record<string, keyof typeof attachmentTypeCodeMap> = {
  '1': 'drawing',
  '2': 'tender',
  '3': 'other',
  drawing: 'drawing',
  '产品图纸': 'drawing',
  tender: 'tender',
  '招标文件': 'tender',
  other: 'other',
  '其它文件': 'other',
  '其他文件': 'other'
}

const templates = ref<any[]>([])
const templateLoading = ref(false)
const templatesLoaded = ref(false)

const templateOptions = computed(() =>
  templates.value.map((t: any) => {
    const name = t.template_name || '模板'
    const no = t.template_no || ''
    const v =
      t.version != null && t.version !== ''
        ? formatCostTemplateVersion(t.version)
        : ''
    const label = no
      ? v
        ? `${name}（${no} · V${v}）`
        : `${name}（${no}）`
      : v
        ? `${name}（V${v}）`
        : name
    return { value: t.template_no, label }
  })
)

const normalizeUnitCode = (value?: string | null) => {
  const text = String(value ?? '').trim()
  if (!text) return ''
  const matched = unitOptions.value.find((u) => u.value === text || u.label === text || u.name === text)
  return matched?.value || text
}

const normalizeSupplierRequiredCode = (field: any) => {
  const raw = field?.supplier_required ?? field?.supplierRequiredCode ?? field?.supplier_behavior ?? field?.supplierBehavior
  const code = Number(raw)
  if (Number.isInteger(code) && code >= 0 && code <= 6) return code
  if (typeof raw === 'string' && raw in supplierBehaviorCodeMap) return supplierBehaviorCodeMap[raw]
  return 0
}

const loadCompanyOptions = async () => {
  companyLoading.value = true
  try {
    const res = await GetCompanies({ page: 1, page_size: 500, pageSize: 500 })
    const list =
      res?.data?.data?.results ||
      res?.data?.results ||
      res?.data?.list ||
      res?.data ||
      res?.results ||
      res?.list ||
      []
    companyOptions.value = (Array.isArray(list) ? list : []).map((c: any) => ({
      value: c.company_code,
      label: c.company_short_name || c.company_code || c.company_name || '厂区'
    }))
  } catch (e) {
    console.warn('加载交易厂区失败', e)
    companyOptions.value = []
  } finally {
    companyLoading.value = false
  }
}

const extractTaxRate = (obj: any) => {
  const keys = ['taxRate', 'tax_rate', 'tax', 'taxrate', 'tax_ratio', 'taxratio', 'rate']
  for (const k of keys) {
    if (obj && obj[k] !== undefined && obj[k] !== null && obj[k] !== '') {
      const n = Number(obj[k])
      return Number.isFinite(n) ? n : obj[k]
    }
  }
  return undefined
}

const loadCurrencyOptions = async (factory?: string) => {
  if (!factory) {
    currencyOptions.value = []
    return
  }
  currencyLoading.value = true
  try {
    const res = await GetCurrencies({ page: 1, page_size: 50, pageSize: 50, factory })
    const list =
      res?.data?.data?.results ||
      res?.data?.results ||
      res?.data?.list ||
      res?.data ||
      res?.results ||
      res?.list ||
      []
    currencyOptions.value = (Array.isArray(list) ? list : []).map((c: any) => ({
      value: c.currencycode || c.currency_code || c.code || c.currency,
      label: c.currencyname || c.currency_name || c.currencycode || c.code || '币别',
      taxRate: extractTaxRate(c)
    }))
  } catch (e) {
    console.warn('加载币别失败', e)
    currencyOptions.value = []
  } finally {
    currencyLoading.value = false
  }
}

const loadPartOptions = async () => {
  partLoading.value = true
  try {
    const res = await GetParts({ page: 1, page_size: 500, pageSize: 500 })
    const list =
      res?.data?.data?.results ||
      res?.data?.results ||
      res?.data?.list ||
      res?.data ||
      res?.results ||
      res?.list ||
      []
    partOptions.value = (Array.isArray(list) ? list : []).map((p: any) => ({
      value: p.partid || p.part_no || p.partid_code || p.code,
      label: `${p.partid || p.part_no || p.code || ''}${p.partid_name ? ` - ${p.partid_name}` : ''}`.trim(),
      name: p.partid_name || p.part_name || p.name,
      unit: p.unit || p.uom || ''
    }))
  } catch (e) {
    console.warn('加载料号失败', e)
    partOptions.value = []
  } finally {
    partLoading.value = false
  }
}

const loadMaterialOptions = async (factory?: string) => {
  materialLoading.value = true
  try {
    const params: any = { page: 1, page_size: 300, pageSize: 300 }
    if (factory) params.factory = factory
    const res = await GetMaterials(params)
    const list =
      res?.data?.data?.results ||
      res?.data?.results ||
      res?.data?.list ||
      res?.data ||
      res?.results ||
      res?.list ||
      []
    materialOptions.value = (Array.isArray(list) ? list : []).map((m: any) => ({
      value: m.materialtype || m.material || m.name,
      label: m.materialtype || m.material || m.name,
      density: m.density || m.specificgravity,
      price: m.price
    }))
  } catch (e) {
    console.warn('加载材质信息失败', e)
    materialOptions.value = []
  } finally {
    materialLoading.value = false
  }
}

const loadStationOptions = async (factory?: string) => {
  stationLoading.value = true
  try {
    const params: any = { page: 1, page_size: 500, pageSize: 500 }
    if (factory) params.factory = factory
    const res = await GetStations(params)
    const list =
      res?.data?.data?.results ||
      res?.data?.results ||
      res?.data?.list ||
      res?.data ||
      res?.results ||
      res?.list ||
      []
    stationOptions.value = (Array.isArray(list) ? list : []).map((s: any) => ({
      value: s.stationcode || s.station_code || s.stationname || s.name,
      label: `${s.stationname || s.name || s.stationcode || ''}${s.stationcode ? `（${s.stationcode}）` : ''}`,
      rate: s.rate,
      unit: normalizeUnitCode(s.unit || s.process_unit || s.uom || s.station_unit)
    }))
  } catch (e) {
    console.warn('加载加工工站失败', e)
    stationOptions.value = []
  } finally {
    stationLoading.value = false
  }
}

const loadUnitOptions = async (factory?: string) => {
  unitLoading.value = true
  try {
    const params: any = { page: 1, page_size: 500, pageSize: 500 }
    if (factory) params.factory = factory
    const res = await GetUnits(params)
    const list =
      res?.data?.data?.results ||
      res?.data?.results ||
      res?.data?.list ||
      res?.data ||
      res?.results ||
      res?.list ||
      []
    unitOptions.value = (Array.isArray(list) ? list : []).map((u: any) => {
      const code = String(u.unitcode || u.unit_code || u.unit || u.code || '').trim()
      const name = String(u.unitname || u.unit_name || '').trim()
      const value = code || name
      return {
        value,
        label: value,
        name
      }
    })
  } catch (e) {
    console.warn('加载计量单位失败', e)
    unitOptions.value = []
  } finally {
    unitLoading.value = false
  }
}

const loadSupplierOptions = async (factory?: string) => {
  supplierLoading.value = true
  try {
    const params: any = { page: 1, page_size: 500, pageSize: 500 }
    if (factory) params.factory = factory
    const res = await GetSuppliers(params)
    const list =
      res?.data?.data?.results ||
      res?.data?.results ||
      res?.data?.list ||
      res?.data ||
      res?.results ||
      res?.list ||
      []
    const filtered = (Array.isArray(list) ? list : []).filter((s: any) => {
      if (!factory) return true
      return supplierFactoryKeys.some((k) => (s?.[k] || '') === factory)
    })
    supplierOptions.value = filtered.map((s: any) => ({
      value: s.supplier_id || s.supplier_code || s.supplier_name,
      label: `${s.supplier_short_name || s.supplier_name || s.supplier_id || '供应商'}${s.supplier_id ? `（${s.supplier_id}）` : ''}`,
      supplier_code: s.supplier_id || s.supplier_code,
      supplier_name: s.supplier_name || s.supplier_short_name,
      contact: s.contact_person || s.contact || s.linkman,
      email: s.contact_email || s.email,
      factory: supplierFactoryKeys.map((k) => s?.[k]).find((v) => v)
    }))
  } catch (e) {
    console.warn('加载供应商失败', e)
    supplierOptions.value = []
  } finally {
    supplierLoading.value = false
  }
}

const normalizeSections = (sections: any) => {
  if (typeof sections === 'string') {
    try {
      const parsed = JSON.parse(sections)
      return Array.isArray(parsed) ? parsed : []
    } catch (e) {
      console.warn('模版 sections 解析失败', e)
      return []
    }
  }
  return Array.isArray(sections) ? sections : []
}

const parseOptionJson = (value: unknown, label: string) => {
  try {
    return normalizeDict(value, label)
  } catch (e) {
    console.warn(`${label} 解析失败`, e)
    return {}
  }
}

const hasTemplateSections = (tpl: any) => {
  const sections = normalizeSections(tpl?.sections)
  return Array.isArray(sections) && sections.length > 0
}

const costCategoryToTitle: Record<string, string> = {
  '1': '材料成本',
  '2': '加工成本',
  '3': '其它成本',
  '4': '管销研费用',
  '5': '利润',
  '6': '税金',
  '7': '产品明细'
}

const buildSectionsFromCostTemplate = (head: any) => {
  const items = Array.isArray(head?.items) ? head.items : []
  if (!items.length) return []
  const group = new Map<string, any[]>()
  items.forEach((it: any) => {
    const cat = String(it.cost_category ?? '')
    const title = costCategoryToTitle[cat] || '其它成本'
    if (!group.has(title)) group.set(title, [])
    group.get(title)!.push(it)
  })
  const order = ['产品明细', '材料成本', '加工成本', '其它成本', '管销研费用', '利润', '税金']
  return order
    .filter((t) => group.has(t))
    .map((title) => {
      const rows = (group.get(title) || []).slice().sort((a: any, b: any) => (a.item_order || 0) - (b.item_order || 0))
      return {
        id: title,
        title,
        enabled: true,
        // supplierCanAddRow:
          // title === '材料成本'
            // ? Number(head?.is_can_add_materials || 0) === 1
            // : title === '加工成本'
            //   ? Number(head?.is_can_add_process || 0) === 1
            //   : false,
        fields: rows.map((r: any) => ({
          key: r.item_no || '',
          label: r.item_name_cn || r.item_no || '',
          autoFill: Number(r.is_computed || 0) === 1,
          purchaserRequired: Number(r.purchaser_required || 0) === 1,
          supplierRequiredCode: normalizeSupplierRequiredCode(r)
        }))
      }
    })
}

const fetchTemplateDetailIfNeeded = async (tpl: any) => {
  if (!tpl) return tpl
  if (hasTemplateSections(tpl)) return tpl
  if (!tpl?.id) return tpl
  try {
    const res = await costTemplateApi.GetObj(tpl.id)
    const head = res?.data?.data || res?.data || res
    if (head && typeof head === 'object') {
      const sections = buildSectionsFromCostTemplate(head)
      const merged = { ...tpl, ...head, sections }
      const idx = templates.value.findIndex((t: any) => t.id === tpl.id)
      if (idx >= 0) templates.value[idx] = merged
      return merged
    }
  } catch (e) {
    console.warn('加载成本结构模板详情失败', e)
  }
  return tpl
}

const allowedSectionsForTemplate = (tpl: any) => {
  const base = tpl && String(tpl.is_bom || 'Y') === 'Y' ? costEnabledSections : costDisabledSections
  const tplSections = normalizeSections(tpl?.sections)
  const templateSections = tplSections
    .filter((s: any) => s?.enabled !== false)
    .map((s: any) => s.title || s.name || '')
    .filter(Boolean)
  const allowed = templateSections.length ? base.filter((t) => templateSections.includes(t)) : base
  return allowed.length ? allowed : base
}

const buildSectionAddConfig = (tpl: any) => {
  const allowed = allowedSectionsForTemplate(tpl)
  const map: Record<string, boolean> = {}
  const sections = normalizeSections(tpl?.sections)
  sections.forEach((s: any) => {
    const title = s.title || s.name || ''
    if (title && allowed.includes(title)) {
      // map[title] = title === '其它成本' ? false : !!s.supplierCanAddRow
      // `supplierCanAddRow` 来源于模板的供应商报价配置，不应用于采购端询价单编辑页。
      map[title] = title === '材料成本' || title === '加工成本'
    }
  })
  // 业务要求：其它成本不允许新增行
  if (allowed.includes('其它成本')) {
    map['其它成本'] = false
  }
  return map
}

const buildRowsFromTemplate = (tpl: any) => {
  const allowed = allowedSectionsForTemplate(tpl)
  const rows: CostRow[] = []
  const sections = normalizeSections(tpl?.sections)
  allowed.forEach((title: string, idx: number) => {
    const sec = sections.find((s: any) => (s.title || s.name || '') === title) || {}
    const values: Record<string, any> = {}
    if (Array.isArray(sec.fields)) {
      sec.fields.forEach((f: any) => {
        values[f.key] = f.default ?? ''
      })
    }
    rows.push({ id: `tpl-${sec.id || title}-${idx}-${Date.now()}`, section: title, field: `tpl-${sec.id || title}-${idx}`, values })
  })
  if (!rows.length) {
    return costDisabledSections.map((title, idx) => ({ id: `def-${idx}-${Date.now()}`, section: title, field: `def-${idx}`, values: {} }))
  }
  return rows
}

type CostFieldColumn = { key: string; label: string; autoFill?: boolean; purchaserRequired?: boolean; supplierRequiredCode?: number }
type CostRow = { id: string; section: string; field: string; values: Record<string, any> }

const costRows = ref<CostRow[]>([])
const sectionAddConfig = ref<Record<string, boolean>>({})

const dialog = reactive({ visible: false, mode: 'create' as 'create' | 'edit' | 'view', currentId: null as number | null })
const isViewMode = computed(() => dialog.mode === 'view')

const dialogTitle = computed(() => {
  if (dialog.mode === 'create') return '新增询价单'
  if (dialog.mode === 'view') return '查看询价单'
  return '编辑询价单'
})
const activeTab = ref('base')
const skipTemplateWatch = ref(false)
let handlingPlantChange = false
const userStore = useUserInfo()
/** 与主表 `purchase_dept` CharField(max_length=20) 一致 */
const PURCHASE_DEPT_MAX_LEN = 20
const clipPurchaseDept = (raw: unknown) => {
  const s = String(raw ?? '').trim()
  if (!s) return ''
  return s.length > PURCHASE_DEPT_MAX_LEN ? s.slice(0, PURCHASE_DEPT_MAX_LEN) : s
}
const loginPurchaseDept = () => clipPurchaseDept(userStore.userInfos?.dept_info?.dept_name)
const currentUserName = computed(
  () =>
    userStore.userInfos?.name ||
    userStore.userInfos?.username ||
    userStore.userInfos?.email ||
    userStore.userInfos?.nickName ||
    ''
)
const getStatusCode = (value: unknown) => Number(value)
const isOpenStatus = (value: unknown) => getStatusCode(value) === STATUS_OPEN
const isReadonlyStatus = (value: unknown) => [STATUS_CONFIRMED, STATUS_PUBLISHED].includes(getStatusCode(value))
const getErrorMessage = formatRfqApiErrorMessage

const emptyForm = () => ({
  id: null,
  inquiry_no: '',
  title: '',
  // UI展示字段（后端不存）
  product_category: '',
  template: '',
  template_code: '',
  purchase_dept: '',
  is_bom: 0,
  part_no: '',
  part_name: '',
  part_unit: '',
  quote_deadline: '',
  buying_method: 1,
  bid_start_time: '',
  bid_end_time: '',
  purchase_qty: 0,
  buyer: '',
  currency: 'CNY',
  plant: '',
  target_price: 0,
  lead_time_days: 0,
  payment_method: 1,
  status: 1,
  remark: '',
  vendors: [] as any[],
  attachments: { drawing: [], tender: [], other: [] as any[] }
})

const form = reactive(emptyForm())

const isInquiryBuyingMethod = computed(() => Number(form.buying_method) === 1)

watch(
  () => form.buying_method,
  (v) => {
    if (Number(v) === 1) {
      form.bid_start_time = ''
      form.bid_end_time = ''
    } else if (Number(v) === 2) {
      form.quote_deadline = ''
    }
  }
)

const toNumberOrZero = (val: any) => {
  if (val === null || val === undefined || val === '') return 0
  const n = Number(val)
  return Number.isFinite(n) ? n : 0
}

const padTwoDigits = (value: number) => String(value).padStart(2, '0')

const formatQuoteDeadlineValue = (value: Date) =>
  `${value.getFullYear()}-${padTwoDigits(value.getMonth() + 1)}-${padTwoDigits(value.getDate())} ${padTwoDigits(value.getHours())}:00:00`

const normalizeQuoteDeadline = (value: unknown) => {
  if (!value) return ''
  if (value instanceof Date) {
    return Number.isNaN(value.getTime()) ? '' : formatQuoteDeadlineValue(value)
  }
  if (typeof value === 'string') {
    const text = value.trim()
    if (!text) return ''
    const parsed = new Date(text.includes('T') ? text : text.replace(' ', 'T'))
    if (!Number.isNaN(parsed.getTime())) {
      return formatQuoteDeadlineValue(parsed)
    }
    const matched = text.match(/^(\d{4}-\d{2}-\d{2})(?:[ T](\d{2}))?/)
    if (matched) {
      return `${matched[1]} ${matched[2] || '00'}:00:00`
    }
  }
  return ''
}

const formatDateTimeFull = (value: Date) =>
  `${value.getFullYear()}-${padTwoDigits(value.getMonth() + 1)}-${padTwoDigits(value.getDate())} ${padTwoDigits(value.getHours())}:${padTwoDigits(value.getMinutes())}:${padTwoDigits(value.getSeconds())}`

/** 投标时间：保留时分秒，与 `el-date-picker` datetime 的 `YYYY-MM-DD HH:mm:ss` 一致 */
const normalizeDateTime = (value: unknown) => {
  if (!value) return ''
  if (value instanceof Date) {
    return Number.isNaN(value.getTime()) ? '' : formatDateTimeFull(value)
  }
  if (typeof value === 'string') {
    const text = value.trim()
    if (!text) return ''
    const fullMatch = text.match(/^(\d{4}-\d{2}-\d{2})[ T](\d{2}):(\d{2})(?::(\d{2}))?/)
    if (fullMatch) {
      const sec = fullMatch[4] ?? '00'
      return `${fullMatch[1]} ${fullMatch[2]}:${fullMatch[3]}:${sec}`
    }
    const parsed = new Date(text.includes('T') ? text : text.replace(' ', 'T'))
    if (!Number.isNaN(parsed.getTime())) return formatDateTimeFull(parsed)
  }
  return ''
}

const quoteDeadlineHourOptions = Array.from({ length: 24 }, (_, index) => padTwoDigits(index))
const openBaseDate = ref<Date | null>(null)

const getDayStart = (value: Date) => new Date(value.getFullYear(), value.getMonth(), value.getDate())

const parseDate = (value: unknown) => {
  const normalized = normalizeQuoteDeadline(value)
  if (!normalized) return null
  const parsed = new Date(normalized.replace(' ', 'T'))
  return Number.isNaN(parsed.getTime()) ? null : parsed
}

const captureQuoteDeadlineOpenBaseDate = () => {
  openBaseDate.value = getDayStart(new Date())
}

const isQuoteDeadlineDateDisabled = (date: Date) => {
  if (!openBaseDate.value) return false
  return getDayStart(date).getTime() <= openBaseDate.value.getTime()
}

const validateQuoteDeadlineAfterOpenDay = () => {
  if (Number(form.buying_method) === 1) {
    const selectedDate = parseDate(form.quote_deadline)
    if (!selectedDate) {
      ElMessage.error('请选择报价截止时')
      activeTab.value = 'base'
      return false
    }
    if (openBaseDate.value && getDayStart(selectedDate).getTime() <= openBaseDate.value.getTime()) {
      ElMessage.error('报价截止时只能选择大于打开创建/编辑当天的日期')
      activeTab.value = 'base'
      return false
    }
  } else if (Number(form.buying_method) === 2) {
    const selectedBSDate = parseDate(form.bid_start_time)
    const selectedBEDate = parseDate(form.bid_end_time)
    if (!selectedBSDate || !selectedBEDate) {
      ElMessage.error('请完善投标起止时间')
      activeTab.value = 'base'
      return false
    }
    if (selectedBSDate >= selectedBEDate) {
      ElMessage.error('投标截止时间须晚于投标开始时间')
      activeTab.value = 'base'
      return false
    }
    if (openBaseDate.value && getDayStart(selectedBSDate).getTime() <= openBaseDate.value.getTime()) {
      ElMessage.error('投标开始时间只能选择大于打开创建/编辑当天的日期')
      activeTab.value = 'base'
      return false
    }
  }
  return true
}

const quoteDeadlineDate = computed({
  get: () => {
    const normalized = normalizeQuoteDeadline(form.quote_deadline)
    return normalized ? normalized.slice(0, 10) : ''
  },
  set: (value: string) => {
    if (!value) {
      form.quote_deadline = ''
      return
    }
    const currentHour = quoteDeadlineHour.value || '23'
    form.quote_deadline = `${value} ${currentHour}:00:00`
  }
})

const quoteDeadlineHour = computed({
  get: () => {
    const normalized = normalizeQuoteDeadline(form.quote_deadline)
    return normalized ? normalized.slice(11, 13) : '23'
  },
  set: (value: string) => {
    const date = quoteDeadlineDate.value
    if (!date) {
      form.quote_deadline = ''
      return
    }
    form.quote_deadline = `${date} ${value || '00'}:00:00`
  }
})

const bidStartTimeDate = computed({
  get: () => {
    const normalized = normalizeDateTime(form.bid_start_time)
    return normalized ? normalized.slice(0, 10) : ''
  },
  set: (value: string) => {
    if (!value) {
      form.bid_start_time = ''
      return
    }
    const currentHour = bidStartTimeHour.value || '23'
    form.bid_start_time = `${value} ${currentHour}:00:00`
  }
})

const bidStartTimeHour = computed({
  get: () => {
    const normalized = normalizeDateTime(form.bid_start_time)
    return normalized ? normalized.slice(11, 13) : '23'
  },
  set: (value: string) => {
    const date = bidStartTimeDate.value
    if (!date) {
      form.bid_start_time = ''
      return
    }
    form.bid_start_time = `${date} ${value || '00'}:00:00`
  }
})

const bidEndTimeDate = computed({
  get: () => {
    const normalized = normalizeDateTime(form.bid_end_time)
    return normalized ? normalized.slice(0, 10) : ''
  },
  set: (value: string) => {
    if (!value) {
      form.bid_end_time = ''
      return
    }
    const currentHour = bidEndTimeHour.value || '23'
    form.bid_end_time = `${value} ${currentHour}:00:00`
  }
})

const bidEndTimeHour = computed({
  get: () => {
    const normalized = normalizeDateTime(form.bid_end_time)
    return normalized ? normalized.slice(11, 13) : '23'
  },
  set: (value: string) => {
    const date = bidEndTimeDate.value
    if (!date) {
      form.bid_end_time = ''
      return
    }
    form.bid_end_time = `${date} ${value || '00'}:00:00`
  }
})

const currentTemplate = computed(() => templates.value.find((t: any) => t.template_no === form.template))
const templateSectionMap = computed(() => {
  const map = new Map<string, any>()
  const sections = normalizeSections(currentTemplate.value?.sections)
  sections.forEach((s: any) => {
    const title = s.title || s.name || ''
    if (title) map.set(title, s)
  })
  return map
})
const templateFieldMetaMap = computed(() => {
  const map = new Map<string, Map<string, { autoFill: boolean; purchaserRequired: boolean; supplierRequiredCode: number }>>()
  const sections = normalizeSections(currentTemplate.value?.sections)
  sections.forEach((section: any) => {
    const title = section.title || section.name || ''
    if (!title) return
    const fieldMap = new Map<string, { autoFill: boolean; purchaserRequired: boolean; supplierRequiredCode: number }>()
    ;(section.fields || []).forEach((field: any) => {
      if (!field?.key) return
      fieldMap.set(field.key, {
        autoFill: Number(field.is_computed ?? field.isComputed ?? field.autoFill ?? 0) === 1 || field.autoFill === true,
        purchaserRequired:
          Number(field.purchaser_required ?? field.purchaserRequired ?? 0) === 1 || field.purchaserRequired === true,
        supplierRequiredCode: normalizeSupplierRequiredCode(field)
      })
    })
    map.set(title, fieldMap)
  })
  return map
})

const enabledSections = computed(() => allowedSectionsForTemplate(currentTemplate.value))
const profitTaxSections = computed(() => enabledSections.value.filter((s) => profitTaxNames.includes(s)))
const primarySections = computed(() => enabledSections.value.filter((s) => !profitTaxNames.includes(s)))

const statusTagType = (s: unknown) => {
  const status = getStatusCode(s)
  if (status === STATUS_OPEN) return 'info'
  if (status === STATUS_CONFIRMED) return 'success'
  if (status === STATUS_PUBLISHED) return 'warning'
  if (status === 0) return 'danger'
  return 'primary'
}
const statusLabel = (s: unknown) => statusDict.find((i) => i.value === getStatusCode(s))?.label || String(s ?? '')

const partNoHiddenSections = new Set(['加工成本', '其它成本', '利润', '税金'])
const partNoHiddenDisplaySections = new Set(['材料成本', '加工成本', '其它成本', '利润', '税金'])

// 询价单号由后端生成（InquirySerializer._generate_code），前端不再本地生成

const setCurrencyFromOptions = () => {
  const has = currencyOptions.value.find((c) => c.value === form.currency)
  if (!has && currencyOptions.value.length) {
    form.currency = currencyOptions.value[0].value
  }
  if (!currencyOptions.value.length) {
    form.currency = ''
  }
}

const applyTaxRateFromCurrency = () => {
  const currency = currencyOptions.value.find((c) => c.value === form.currency)
  if (!currency) return
  const tax = currency.taxRate
  if (tax === undefined) return
  costRows.value
    .filter((r) => r.section === '税金')
    .forEach((r) => {
      if (!r.values) r.values = {}
      const key = pickKey(r.values, taxRateKeys, 'taxRate')
      r.values[key] = tax
    })
}

const applyTemplateMeta = (tpl: any) => {
  if (!tpl) return
  form.is_bom = String(tpl.is_bom || 'Y') === 'Y' ? 1 : 0
  form.template_code = tpl.template_no || form.template_code
}

const handlePlantChange = async (val?: string) => {
  if (handlingPlantChange) return
  handlingPlantChange = true
  try {
    if (val !== undefined && val !== form.plant) {
      form.plant = val || ''
    } else if (!val) {
      form.plant = ''
    }
    await Promise.all([
      loadCurrencyOptions(form.plant),
      loadMaterialOptions(form.plant),
      loadStationOptions(form.plant),
      loadUnitOptions(form.plant),
      loadSupplierOptions(form.plant)
    ])
    if (form.plant) {
      setCurrencyFromOptions()
      applyTaxRateFromCurrency()
    } else {
      form.currency = ''
    }
  } finally {
    handlingPlantChange = false
  }
}

const applyPartNoToCostRows = (partNo?: string) => {
  if (!partNo) return
  costRows.value.forEach((r) => {
    if (partNoHiddenSections.has(r.section)) {
      r.values = { ...r.values, partNo }
    }
  })
}

const handlePartChange = (val?: string) => {
  const current = partOptions.value.find((p) => p.value === val)
  form.part_no = val || ''
  if (current?.name) {
    form.part_name = current.name
  }
  form.part_unit = current?.unit || ''
  applyPartNoToCostRows(val)
}

const toNumber = (v: any) => {
  const n = Number(v)
  return Number.isFinite(n) ? n : 0
}

/** 提交材料行数量：空则 null；是否必填由成本模板 purchaser_required 与前端校验共同约束，不默认用采购数量填充。 */
const normalizeMaterialQtyForSubmit = (v: any) => {
  if (v === '' || v === null || v === undefined) return null
  const n = Number(v)
  if (!Number.isFinite(n)) return null
  return Math.trunc(n)
}

const pickKey = (values: Record<string, any>, candidates: string[], fallback: string) => {
  for (const k of candidates) {
    if (k in values) return k
  }
  return fallback
}

const isTemplateComputedField = (section: string, key: string) => {
  return templateFieldMetaMap.value.get(section)?.get(key)?.autoFill === true
}

const isCostFieldReadonly = (section: string, key: string) => {
  return isViewMode.value || isTemplateComputedField(section, key)
}

const isEmptyRequiredValue = (value: any) => value === null || value === undefined || value === ''

const validatePurchaserRequiredFields = () => {
  for (const section of enabledSections.value) {
    const requiredColumns = (sectionColumns.value[section] || []).filter((col) => col.purchaserRequired)
    if (!requiredColumns.length) continue
    const rows = groupedCostRows.value[section] || []
    for (let rowIndex = 0; rowIndex < rows.length; rowIndex += 1) {
      const row = rows[rowIndex]
      for (const col of requiredColumns) {
        if (isEmptyRequiredValue(row?.values?.[col.key])) {
          activeTab.value = 'cost'
          ElMessage.error(`${section} 第${rowIndex + 1}行【${col.label}】为采购必填项`)
          return false
        }
      }
    }
  }
  return true
}

const updateMaterialCalc = (row: CostRow) => {
  if (row.section !== '材料成本') return
  if (!row.values) row.values = {}
  const v = row.values
  const length = toNumber(v.length)
  const width = toNumber(v.width)
  const height = toNumber(v.height)
  const sg = toNumber(v.specificgravity)
  const qty = toNumber(v.qty ?? v.quantity ?? v.num ?? v.count ?? form.purchase_qty)
  const unitPrice = toNumber(v.unitPrice ?? v.unitprice ?? v.price ?? v.unit_price)
  const weightKey = pickKey(v, weightKeys, 'weight')
  const feeKey = pickKey(v, materialFeeKeys, 'material_cost')
  const weight = length * width * height * sg * qty
  v[weightKey] = Number(weight.toFixed(4))
  const materialFee = v[weightKey] * unitPrice
  v[feeKey] = Number(materialFee.toFixed(4))
}

const handleMaterialSelect = (row: CostRow, value?: string) => {
  if (!row.values) row.values = {}
  row.values.material = value || ''
  const material = materialOptions.value.find((m) => m.value === value)
  if (material) {
    if (material.density !== undefined) {
      row.values.specificgravity = material.density
    }
    if (material.price !== undefined) {
      const priceKey = pickKey(row.values, priceKeys, 'unitPrice')
      row.values[priceKey] = material.price
    }
  }
  updateMaterialCalc(row)
}

const updateProcessCalc = (row: CostRow) => {
  if (row.section !== '加工成本') return
  if (!row.values) row.values = {}
  const v = row.values
  const rateKey = pickKey(v, processRateKeys, 'unitrate')
  const rate = toNumber(v[rateKey])
  const qtyKey = pickKey(v, processQtyKeys, 'processqty')
  const qty = toNumber(v[qtyKey])
  const feeKey = pickKey(v, processFeeKeys, 'processprice')
  v[feeKey] = Number((rate * qty).toFixed(4))
}

/** 与下拉 option.value、v-model(row.name) 一致，用于去重 */
const vendorRowSelectKey = (row: any) =>
  String(row?.name ?? row?.supplier_id ?? row?.supplier_code ?? '').trim()

/** 其它行已选中的供应商不再出现在本行下拉中（避免重复违反唯一约束） */
const supplierOptionsForVendorRow = (row: any) => {
  const taken = new Set<string>()
  for (const v of form.vendors || []) {
    if (v === row) continue
    const k = vendorRowSelectKey(v)
    if (k) taken.add(k)
  }
  const self = vendorRowSelectKey(row)
  return supplierOptions.value.filter((s) => {
    const k = String(s.value ?? '').trim()
    if (!k) return false
    if (self && k === self) return true
    return !taken.has(k)
  })
}

const handleVendorSelect = (row: any, value?: string) => {
  row.name = value || ''
  const supplier = supplierOptions.value.find((s) => s.value === value)
  if (supplier) {
    row.supplier_id = value || ''
    row.supplier_code = supplier.supplier_code || value || ''
    row.supplier_name = supplier.supplier_name || supplier.label || ''
    if (supplier.contact) {
      row.contact = supplier.contact
    }
    if (supplier.email) {
      row.email = supplier.email
    }
  }
}

const handleStationSelect = (row: CostRow, value?: string) => {
  if (!row.values) row.values = {}
  row.values.process_station = value || ''
  const station = stationOptions.value.find((s) => s.value === value)
  if (station && station.rate !== undefined) {
    const rateKey = pickKey(row.values, processRateKeys, 'unitrate')
    row.values[rateKey] = station.rate
  }
  if (station && station.unit) {
    const unitKey = pickKey(row.values, processUnitKeys, 'unit')
    row.values[unitKey] = normalizeUnitCode(station.unit)
  }
  updateProcessCalc(row)
}

const resetForm = () => {
  Object.assign(form, emptyForm())
  costRows.value = []
  sectionAddConfig.value = {}
  activeTab.value = 'base'
}

const openCreate = async () => {
  captureQuoteDeadlineOpenBaseDate()
  await Promise.all([ensureTemplatesLoaded(), loadCompanyOptions(), loadPartOptions()])
  dialog.mode = 'create'
  dialog.currentId = null
  resetForm()
  if (currentUserName.value) {
    form.buyer = currentUserName.value
  }
  form.purchase_dept = loginPurchaseDept()
  if (companyOptions.value.length && !form.plant) {
    form.plant = companyOptions.value[0].value
  }
  if (form.plant) {
    await handlePlantChange(form.plant)
  }
  if (templates.value.length) {
    skipTemplateWatch.value = true
    const tpl = templates.value[0]
    form.template = tpl.template_no
    applyTemplateMeta(tpl)
    await loadCostItemsFromTemplate(tpl, true)
  } else {
    await loadCostItemsFromTemplate(null, true)
  }
  dialog.visible = true
}

const openDetail = async (row: any, mode: 'edit' | 'view') => {
  if (mode === 'edit') {
    captureQuoteDeadlineOpenBaseDate()
  }
  await Promise.all([ensureTemplatesLoaded(), loadCompanyOptions(), loadPartOptions()])
  const nextMode = mode === 'edit' && isReadonlyStatus(row?.status) ? 'view' : mode
  if (mode === 'edit' && nextMode === 'view') {
    ElMessage.warning('确认状态禁止编辑，已为您切换为查看模式。')
  }
  dialog.mode = nextMode
  dialog.currentId = row.id
  skipTemplateWatch.value = true
  // 以详情接口为准，避免列表字段缺失导致子表/字段不同步
  let detail = row
  try {
    const res = await api.GetObj(row.id)
    detail = unwrapResponseData(res) || row
  } catch (e) {
    detail = row
  }
  const rfqItem = Array.isArray(detail?.rfq_items) && detail.rfq_items.length ? detail.rfq_items[0] : null
  const detailBuyingMethod =
    detail?.buying_method != null && detail?.buying_method !== '' ? Number(detail.buying_method) : 1
  const mappedDetail = {
    ...detail,
    plant: detail?.plant || detail?.company_code || '',
    template: detail?.template_code || detail?.template || '',
    template_code: detail?.template_code || detail?.template || '',
    part_no: detail?.part_no || rfqItem?.part_id || '',
    part_name: detail?.part_name || rfqItem?.product_name || '',
    part_unit: detail?.part_unit || rfqItem?.unit || '',
    quote_deadline: normalizeQuoteDeadline(detail?.quote_deadline),
    buying_method: Number.isFinite(detailBuyingMethod) ? detailBuyingMethod : 1,
    bid_start_time:
      Number(detailBuyingMethod) === 1 ? '' : normalizeDateTime(detail?.bid_start_time),
    bid_end_time:
      Number(detailBuyingMethod) === 1 ? '' : normalizeDateTime(detail?.bid_end_time),
    purchase_qty: detail?.purchase_qty ?? rfqItem?.qty ?? 0,
    target_price: detail?.target_price ?? detail?.inquiry_price ?? rfqItem?.unit_price ?? 0
  }
  Object.assign(form, emptyForm(), mappedDetail)
  ;['purchase_qty', 'target_price', 'lead_time_days'].forEach((k) => {
    ;(form as any)[k] = toNumberOrZero((form as any)[k])
  })
  let tpl =
    templates.value.find((t: any) => t.template_no === form.template) ||
    templates.value.find((t: any) => t.template_no === row.template || t.template_no === row.template_code)
  if (tpl) {
    tpl = await fetchTemplateDetailIfNeeded(tpl)
    form.template = tpl.template_no
    applyTemplateMeta(tpl)
  }
  await handlePlantChange(form.plant)
  // 编辑态仅以后端真实子表回填，不再兼容旧 cost_items 大字段
  const buildCostRowsFromDetail = (detailObj: any) => {
    const rows: CostRow[] = []
    const partId = detailObj?.rfq_items?.[0]?.part_id || detailObj?.part_no || detailObj?.part_id || ''
    if (Array.isArray(detailObj?.rfq_items) && detailObj.rfq_items.length) {
      const rfq = detailObj.rfq_items[0]
      const values: any = parseOptionJson(rfq.option_json, '产品明细扩展字段')
      const qty = rfq.qty ?? ''
      const unitPrice = rfq.unit_price ?? ''
      values.partNo = rfq.part_id ?? partId
      values.desc = rfq.product_name ?? ''
      values.unit = rfq.unit ?? ''
      values.qty = qty
      values.price = unitPrice
      values.amount =
        qty !== '' && unitPrice !== '' ? Number((Number(qty) * Number(unitPrice)).toFixed(4)) : values.amount ?? ''
      rows.push({
        id: `prd-0-${Date.now()}`,
        section: '产品明细',
        field: 'prd-0',
        values,
      })
    }
    ;(detailObj?.material_costs || []).forEach((m: any, idx: number) => {
      const values: any = parseOptionJson(m.option_json, '材料成本扩展字段')
      values.material = m.material_spec ?? ''
      values.length = m.length ?? ''
      values.width = m.width ?? ''
      values.height = m.height ?? ''
      values.specificgravity = m.specific_gravity ?? ''
      values.qty = m.qty ?? ''
      values.unitPrice = m.unit_price ?? ''
      values.weight = m.weight ?? ''
      values.material_cost = m.material_cost ?? ''
      const row = { id: `mat-${idx}-${Date.now()}`, section: '材料成本', field: `mat-${idx}`, values: { ...values, partNo: partId } }
      updateMaterialCalc(row)
      rows.push(row)
    })
    ;(detailObj?.process_costs || []).forEach((p: any, idx: number) => {
      const values: any = parseOptionJson(p.option_json, '加工成本扩展字段')
      values.process_station = p.process_station ?? ''
      values.unit = normalizeUnitCode(p.unit)
      values.unitrate = p.unit_rate ?? ''
      values.processqty = p.process_qty ?? ''
      values.processprice = p.process_price ?? ''
      const row = { id: `prc-${idx}-${Date.now()}`, section: '加工成本', field: `prc-${idx}`, values: { ...values, partNo: partId } }
      updateProcessCalc(row)
      rows.push(row)
    })
    if (Array.isArray(detailObj?.other_costs) && detailObj.other_costs.length) {
      const o = detailObj.other_costs[0]
      rows.push({
        id: `oth-0-${Date.now()}`,
        section: '其它成本',
        field: 'oth-0',
        values: { packaging_cost: o.packaging_cost ?? '', transportation_cost: o.transportation_cost ?? '', partNo: partId }
      })
    }
    if (Array.isArray(detailObj?.profit_costs) && detailObj.profit_costs.length) {
      const pr = detailObj.profit_costs[0]
      rows.push({
        id: `pft-0-${Date.now()}`,
        section: '利润',
        field: 'pft-0',
        values: { profitRate: pr.profit_rate ?? '', partNo: partId }
      })
      rows.push({
        id: `tax-0-${Date.now()}`,
        section: '税金',
        field: 'tax-0',
        values: { taxRate: pr.tax_rate ?? '', partNo: partId }
      })
    }
    return rows
  }

  const detailCostRows = buildCostRowsFromDetail(detail)
  costRows.value = detailCostRows
  applyTaxRateFromCurrency()
  sectionAddConfig.value = buildSectionAddConfig(tpl)
  // vendors/attachments：仅用新版子表回填
  form.vendors = Array.isArray(detail?.suppliers)
    ? detail.suppliers.map((s: any, idx: number) => ({
      id: s.id || `v-${idx}-${Date.now()}`,
      name: s.supplier_name || '',
      supplier_id: s.supplier_code || '',
      supplier_code: s.supplier_code || '',
      supplier_name: s.supplier_name || '',
      contact: s.contact_person || '',
      email: s.contact_email || '',
      phone: s.contact_phone || ''
    }))
    : []
  const next = { drawing: [], tender: [], other: [] as any[] }
  if (Array.isArray(detail?.attachments)) {
    detail.attachments.forEach((a: any) => {
      const type = attachmentTypeKeyMap[String(a.file_type ?? '3')] || 'other'
      if (!next[type as keyof typeof next]) return
      ;(next as any)[type].push({ name: a.file_name, url: a.file_path, status: 'ready' })
    })
  }
  form.attachments = next
  applyPartNoToCostRows(form.part_no)
  activeTab.value = 'base'
  dialog.visible = true
}

const openEdit = (row: any) => openDetail(row, 'edit')
const openView = (row: any) => openDetail(row, 'view')

type ComparisonDetailRow = {
  label: string
  values: Record<string, any>
  avg?: number
  min?: number
  /** 与成本模板字段一致：文本列走 displayTextEmpty */
  isText?: boolean
}
/** 材料/加工：按材质或工站分组，组内多行明细（对齐 bargain_price.html 展开结构） */
type ComparisonDetailGroup = { title: string; lines: ComparisonDetailRow[] }
type ComparisonRow = ComparisonDetailRow & {
  key: string
  details?: ComparisonDetailRow[]
  detailGroups?: ComparisonDetailGroup[]
}

const compareTableRef = ref()
/** el-table 内 el-input 在异步合并 values 后常不重绘，递增 key 强制刷新 */
const compareTableRenderKey = ref(0)
const expandedRowKeys = ref<string[]>([])

const comparisonDialog = reactive({
  visible: false,
  loading: false,
  title: '',
  currentRow: null as any,
  quotes: [] as any[],
  baseInfo: {
    code: '',
    partNo: '',
    partName: '',
    targetPrice: '',
    currency: '',
    taxRate: '',
    dealPrice: '',
    lowestProcessPrice: ''
  },
  suppliers: [] as { name: string; code: string; quotationId?: number | string }[],
  rows: [] as ComparisonRow[]
})

const QUOTATION_STATUS_LABELS: Record<number, string> = {
  1: '待报价',
  2: '报价中',
  3: '已报价',
  4: '已过期'
}

const quotationPreview = reactive({
  visible: false,
  loading: false,
  title: '',
  quote: null as any
})

const quotationPreviewRfqItem = computed(() => {
  const q = quotationPreview.quote
  if (!q?.rfq_items?.length) return null
  return q.rfq_items[0]
})

const quotationPreviewCurrency = computed(() => {
  const q = quotationPreview.quote as any
  const c = q?.currency ?? q?.transaction_currency
  if (c != null && c !== '') return String(c)
  return displayTextEmpty(comparisonDialog.baseInfo.currency)
})

/**
 * 基本信息「税费」：金额（含税−不含税，或上阶物料明细 tax_rate 字段——库中存的是税费金额，非比例）
 */
const quotationPreviewTaxDisplay = computed(() => {
  const it = quotationPreviewRfqItem.value as any
  if (!it) return displayNumericEmpty(null)
  const inc = it.total_price_incl_tax
  const ex = it.total_price_excl_tax
  if (inc != null && inc !== '' && ex != null && ex !== '') {
    const ni = Number(inc)
    const ne = Number(ex)
    if (Number.isFinite(ni) && Number.isFinite(ne)) return displayNumericEmpty(ni - ne)
  }
  return displayNumericEmpty(it.tax_rate)
})

/** ⑤ 税金「税率」：仅来自 profit_costs（税率比例）；勿与 rfq_items.tax_rate（税费金额）混用 */
const quotationPreviewTaxTableRows = computed(() => {
  const q = quotationPreview.quote as any
  if (!q) return []
  const list = q.tax_costs
  if (Array.isArray(list) && list.length) return list
  const pid = quotationPreviewRfqItem.value?.part_id
  const profits = q.profit_costs
  const pc =
    pid && Array.isArray(profits)
      ? profits.find((p: any) => p.part_id === pid) || profits[0]
      : profits?.[0]
  return [{ tax_rate: pc?.tax_rate }]
})

const quotationPreviewStatusLabel = computed(() => {
  const s = Number((quotationPreview.quote as any)?.status)
  if (!Number.isFinite(s)) return '-'
  return QUOTATION_STATUS_LABELS[s] ?? String(s)
})

const quotationPreviewTotalPrice = computed(() => {
  const q = quotationPreview.quote as any
  if (!q) return '0.00'
  const a = q.quote_amount
  if (a !== undefined && a !== null && a !== '') {
    return displayNumericEmpty(a)
  }
  const it = q.rfq_items?.[0]
  if (it?.total_price_incl_tax != null && it?.total_price_incl_tax !== '') {
    return displayNumericEmpty(it.total_price_incl_tax)
  }
  return '0.00'
})

const openQuotationPreview = async (supplierIndex: number) => {
  let quote: any = comparisonDialog.quotes[supplierIndex]
  const sup = comparisonDialog.suppliers[supplierIndex]
  if (!quote && sup?.quotationId != null) {
    quotationPreview.loading = true
    quotationPreview.quote = null
    quotationPreview.title = `报价单预览 · ${sup?.name || ''}`
    quotationPreview.visible = true
    try {
      const res = await getQuotationDetail(sup.quotationId)
      quote = unwrapQuotationDetail(res)
    } catch (e: any) {
      ElMessage.error(e?.message || '加载报价单失败')
      quotationPreview.visible = false
      return
    } finally {
      quotationPreview.loading = false
    }
  }
  if (!quote) {
    ElMessage.warning('暂无该供应商报价单数据')
    return
  }
  quotationPreview.quote = quote
  quotationPreview.title = `报价单预览 · ${quote.supplier_name || sup?.name || ''}（${quote.quotation_no || ''}）`
  quotationPreview.visible = true
}

const comparisonInquiryStatus = computed(() => Number(comparisonDialog.currentRow?.status))

/** 比价主表：利润/税金行为金额合计，与材料成本等同用两位小数，不加 %（仅表头「税率」用 displayPercentRate） */
const formatComparisonMainCell = (row: ComparisonRow, v: unknown) => {
  if (row.key === 'rank') {
    if (v === null || v === undefined || v === '') return '-'
    return String(v)
  }
  if (v === null || v === undefined || v === '' || v === '-') return '0.00'
  const n = Number(v)
  if (Number.isFinite(n)) return n.toFixed(2)
  return String(v)
}

const formatCompareAvg = (v: unknown, _rowKey?: string) => {
  if (v === undefined || v === null) return '0.00'
  const n = Number(v)
  if (Number.isFinite(n)) return n.toFixed(2)
  return String(v)
}

const formatCompareMin = (v: unknown, _rowKey?: string) => {
  if (v === undefined || v === null) return '0.00'
  const n = Number(v)
  if (Number.isFinite(n)) return n.toFixed(2)
  return String(v)
}

const extractQuotationList = (res: any): any[] => {
  const raw = res?.data?.results ?? res?.data?.data?.results ?? res?.data?.list ?? res?.data
  return Array.isArray(raw) ? raw : []
}

const unwrapQuotationDetail = (res: any) => {
  const d = res?.data
  if (d && typeof d === 'object' && d.data != null) return d.data
  return d
}

const quotationSupplierKey = (quote: any, idx: number) =>
  quote?.supplier_name ||
  quote?.supplierName ||
  quote?.supplier_code ||
  quote?.supplierCode ||
  quote?.autoid ||
  quote?.id ||
  `sup-${idx}`

/** 议价金额回显：保留接口字符串精度，避免 Number 化丢小数位 */
const formatBargainDisplayValue = (bp: any): string => {
  if (bp === null || bp === undefined || bp === '') return ''
  if (typeof bp === 'string') {
    const t = bp.trim()
    return t
  }
  const n = Number(bp)
  if (Number.isFinite(n)) return String(n)
  return String(bp)
}

const hasBargainPrice = (bp: any): boolean => {
  if (bp === null || bp === undefined || bp === '') return false
  if (typeof bp === 'number') return Number.isFinite(bp)
  const n = Number(bp)
  return Number.isFinite(n) || (typeof bp === 'string' && bp.trim() !== '')
}

const mergeNegotiationIntoComparisonRows = (
  rows: ComparisonRow[],
  quotes: any[],
  negList: any[]
) => {
  if (!Array.isArray(negList) || !negList.length) return
  const byQuotationNo = new Map<string, any>()
  const byCode = new Map<string, any>()
  negList.forEach((r) => {
    const qn = String(r.quotation_no || '').trim()
    const c = String(r.supplier_code || '').trim()
    if (qn) byQuotationNo.set(qn, r)
    if (c) byCode.set(c, r)
  })
  const bargainRow = rows.find((r) => r.key === 'bargain')
  const awardRow = rows.find((r) => r.key === 'award')
  const keys = quotes.map((q, idx) => quotationSupplierKey(q, idx))
  const bargainNext = bargainRow?.values ? { ...bargainRow.values } : {}
  const awardNext = awardRow?.values ? { ...awardRow.values } : {}
  quotes.forEach((quote, idx) => {
    const qn = String(quote.quotation_no || quote.quotationNo || '').trim()
    const code = String(quote.supplier_code || quote.supplierCode || '').trim()
    const rec = (qn && byQuotationNo.get(qn)) || (code ? byCode.get(code) : null)
    if (!rec) return
    const name = keys[idx]
    const bp = rec.bargaining_price
    bargainNext[name] = hasBargainPrice(bp) ? formatBargainDisplayValue(bp) : ''
    awardNext[name] = Number(rec.is_awarded) === 1 ? '是' : '否'
  })
  if (bargainRow) bargainRow.values = bargainNext
  if (awardRow) awardRow.values = awardNext
}

/** 合并议价数据后整体替换行引用，避免 el-table 单元格内 el-input 不随异步赋值更新 */
const applyComparisonRowsAfterNegotiationMerge = async (rows: ComparisonRow[]) => {
  comparisonDialog.rows = rows.map((r) => ({
    ...r,
    values: { ...r.values },
    details: r.details ? r.details.map((d) => ({ ...d, values: { ...d.values } })) : undefined,
    detailGroups: r.detailGroups
      ? r.detailGroups.map((g) => ({
          ...g,
          lines: g.lines.map((l) => ({ ...l, values: { ...l.values } }))
        }))
      : undefined
  }))
  await nextTick()
  compareTableRenderKey.value += 1
}

const calcCompareStats = (values: Record<string, any>) => {
  const nums = Object.values(values || {})
    .map((v: any) => Number(v))
    .filter((v): v is number => Number.isFinite(v))
  if (!nums.length) return { avg: undefined as number | undefined, min: undefined as number | undefined }
  return {
    avg: nums.reduce((a, b) => a + b, 0) / nums.length,
    min: Math.min(...nums)
  }
}

const sumMaterialCost = (q: any): number | null => {
  const rows = q.material_costs || []
  let s = 0
  let ok = false
  for (const r of rows) {
    const n = Number(r.material_cost)
    if (Number.isFinite(n)) {
      s += n
      ok = true
    }
  }
  if (ok) return s
  let s2 = 0
  let ok2 = false
  for (const it of q.rfq_items || []) {
    const n = Number(it.total_material_cost)
    if (Number.isFinite(n)) {
      s2 += n
      ok2 = true
    }
  }
  return ok2 ? s2 : null
}

const sumProcessCost = (q: any): number | null => {
  let s = 0
  let ok = false
  for (const r of q.process_costs || []) {
    const n = Number(r.process_price)
    if (Number.isFinite(n)) {
      s += n
      ok = true
    }
  }
  if (ok) return s
  let s2 = 0
  let ok2 = false
  for (const it of q.rfq_items || []) {
    const n = Number(it.total_processing_cost)
    if (Number.isFinite(n)) {
      s2 += n
      ok2 = true
    }
  }
  return ok2 ? s2 : null
}

const sumOtherCost = (q: any): number | null => {
  let s = 0
  let ok = false
  for (const r of q.other_costs || []) {
    const a = Number(r.packaging_cost)
    const b = Number(r.transportation_cost)
    if (Number.isFinite(a)) {
      s += a
      ok = true
    }
    if (Number.isFinite(b)) {
      s += b
      ok = true
    }
  }
  if (ok) return s
  let s2 = 0
  let ok2 = false
  for (const it of q.rfq_items || []) {
    const n = Number(it.total_other_expense)
    if (Number.isFinite(n)) {
      s2 += n
      ok2 = true
    }
  }
  return ok2 ? s2 : null
}

const sumRfqField = (q: any, field: string): number | null => {
  let s = 0
  let ok = false
  for (const it of q.rfq_items || []) {
    const n = Number(it[field])
    if (Number.isFinite(n)) {
      s += n
      ok = true
    }
  }
  return ok ? s : null
}

const firstRfqField = (q: any, field: string) => {
  const it = (q.rfq_items || [])[0]
  if (!it) return undefined
  const v = it[field]
  return v !== undefined && v !== null && v !== '' ? v : undefined
}

/** 与比价表「总价」行一致，用于按含税总价排名（价低名次靠前） */
const getQuoteTotalNumeric = (q: any): number | null => {
  const a = q?.quote_amount
  if (a !== undefined && a !== null && a !== '') {
    const n = Number(a)
    if (Number.isFinite(n)) return n
  }
  const s = sumRfqField(q, 'total_price_incl_tax')
  if (s != null && Number.isFinite(s)) return s
  return null
}

/** 按总价升序赋名次；同价同名次（1,1,3）；无有效总价显示为 '-' */
const buildRanksByTotal = (quotes: any[], supplierKeys: string[]): Record<string, any> => {
  const out: Record<string, any> = {}
  supplierKeys.forEach((k) => {
    out[k] = '-'
  })
  const entries = supplierKeys
    .map((key, idx) => ({ key, total: getQuoteTotalNumeric(quotes[idx]) }))
    .filter((e): e is { key: string; total: number } => e.total != null && Number.isFinite(e.total))
  entries.sort((a, b) => a.total - b.total)
  let rank = 1
  for (let i = 0; i < entries.length; i++) {
    if (i > 0 && entries[i].total !== entries[i - 1].total) {
      rank = i + 1
    }
    out[entries[i].key] = rank
  }
  return out
}

/** 合并 option_json 扁平字段，便于带出模板扩展列 */
const mergeOptionJsonIntoRow = (row: any): any => {
  if (!row || typeof row !== 'object') return row
  const oj = row.option_json
  if (oj == null || oj === '') return row
  let extra: Record<string, any> = {}
  if (typeof oj === 'string') {
    try {
      const p = JSON.parse(oj)
      if (p && typeof p === 'object') extra = p
    } catch {
      return row
    }
  } else if (typeof oj === 'object') {
    extra = oj as Record<string, any>
  }
  return { ...row, ...extra }
}

/** 比价展开明细：按行标签区分数值(空→0.00)与文本(空→-) */
const formatMetricDetailCell = (v: unknown, label: string, isText?: boolean) => {
  if (isText === true || label === '备注') return displayTextEmpty(v)
  return displayNumericEmpty(v)
}

const formatMetricCell = (v: unknown, isText: boolean) => {
  return isText ? displayTextEmpty(v) : displayNumericEmpty(v)
}

const findMaterialRowBySpec = (q: any, spec: string) => {
  const t = String(spec || '').trim()
  return (q.material_costs || []).find((r: any) => String(r.material_spec || '').trim() === t)
}

const findProcessRowByStation = (q: any, station: string) => {
  const t = String(station || '').trim()
  return (q.process_costs || []).find((r: any) => String(r.process_station || '').trim() === t)
}

/** 无模板或模板无字段时的回退顺序（与旧版硬编码一致） */
const DEFAULT_MATERIAL_COMPARISON_METRICS: ComparisonDetailMetric[] = [
  { label: '用量(重量)', get: (r) => r?.weight, isText: false },
  { label: '长', get: (r) => r?.length, isText: false },
  { label: '宽', get: (r) => r?.width, isText: false },
  { label: '高', get: (r) => r?.height, isText: false },
  { label: '材料单价', get: (r) => r?.unit_price, isText: false },
  { label: '比重', get: (r) => r?.specific_gravity, isText: false },
  { label: '数量', get: (r) => r?.qty, isText: false },
  { label: '材料费用', get: (r) => r?.material_cost, isText: false },
  { label: '备注', get: (r) => r?.remark, isText: true }
]

const DEFAULT_PROCESS_COMPARISON_METRICS: ComparisonDetailMetric[] = [
  { label: '加工计量', get: (r) => r?.process_qty, isText: false },
  { label: '单位', get: (r) => r?.unit, isText: true },
  { label: '费率', get: (r) => r?.unit_rate, isText: false },
  { label: '加工时间', get: (r) => r?.process_time ?? r?.processTime, isText: false },
  { label: '加工费用', get: (r) => r?.process_price, isText: false },
  { label: '备注', get: (r) => r?.remark, isText: true }
]

/** 材料成本展开：按材料规格分组；组内行顺序按成本结构模板 fields */
const buildMaterialDetailGroups = (
  quotes: any[],
  supplierKeys: string[],
  metrics: ComparisonDetailMetric[] = DEFAULT_MATERIAL_COMPARISON_METRICS
): ComparisonDetailGroup[] => {
  const specs = new Set<string>()
  quotes.forEach((q) => {
    ;(q.material_costs || []).forEach((r: any) => {
      specs.add(String(r.material_spec || '').trim() || '材料')
    })
  })
  const sortedSpecs = [...specs].sort()
  const groups: ComparisonDetailGroup[] = []
  for (const spec of sortedSpecs) {
    const lines: ComparisonDetailRow[] = []
    for (const m of metrics) {
      const values: Record<string, any> = {}
      supplierKeys.forEach((sup, idx) => {
        const raw = findMaterialRowBySpec(quotes[idx], spec)
        const merged = mergeOptionJsonIntoRow(raw || {})
        values[sup] = formatMetricCell(m.get(merged), m.isText)
      })
      const allDash = supplierKeys.every((sup) => values[sup] === '-')
      if (allDash) continue
      lines.push({ label: m.label, values, isText: m.isText, ...calcCompareStats(values) })
    }
    if (lines.length) groups.push({ title: spec || '材料', lines })
  }
  return groups
}

/** 加工成本展开：按工站分组；组内行顺序按成本结构模板 fields */
const buildProcessDetailGroups = (
  quotes: any[],
  supplierKeys: string[],
  metrics: ComparisonDetailMetric[] = DEFAULT_PROCESS_COMPARISON_METRICS
): ComparisonDetailGroup[] => {
  const stations = new Set<string>()
  quotes.forEach((q) => {
    ;(q.process_costs || []).forEach((r: any) => {
      stations.add(String(r.process_station || '').trim() || '工站')
    })
  })
  const sorted = [...stations].sort()
  const groups: ComparisonDetailGroup[] = []
  for (const station of sorted) {
    const lines: ComparisonDetailRow[] = []
    for (const m of metrics) {
      const values: Record<string, any> = {}
      supplierKeys.forEach((sup, idx) => {
        const raw = findProcessRowByStation(quotes[idx], station)
        const merged = mergeOptionJsonIntoRow(raw || {})
        values[sup] = formatMetricCell(m.get(merged), m.isText)
      })
      const allDash = supplierKeys.every((s) => values[s] === '-')
      if (allDash) continue
      lines.push({ label: m.label, values, isText: m.isText, ...calcCompareStats(values) })
    }
    if (lines.length) groups.push({ title: station || '工站', lines })
  }
  return groups
}

/** 其它成本：包装费 / 运输费（保持原单层表） */
const buildOtherCostDetails = (quotes: any[], supplierKeys: string[]): ComparisonDetailRow[] => {
  const map = new Map<string, ComparisonDetailRow>()
  quotes.forEach((q, idx) => {
    const sup = supplierKeys[idx]
    for (const r of q.other_costs || []) {
      const pkg = r.packaging_cost
      const tr = r.transportation_cost
      if (pkg !== undefined && pkg !== null && pkg !== '') {
        const label = '包装费'
        if (!map.has(label)) map.set(label, { label, values: {} })
        const n = Number(pkg)
        map.get(label)!.values[sup] = Number.isFinite(n) ? n : pkg
      }
      if (tr !== undefined && tr !== null && tr !== '') {
        const label = '运输费'
        if (!map.has(label)) map.set(label, { label, values: {} })
        const n = Number(tr)
        map.get(label)!.values[sup] = Number.isFinite(n) ? n : tr
      }
    }
  })
  return Array.from(map.values()).map((d) => ({
    ...d,
    ...calcCompareStats(d.values)
  }))
}

const buildComparisonRowsFromPisQuotes = (
  quotes: any[],
  detailOpts?: {
    materialMetrics?: ComparisonDetailMetric[]
    processMetrics?: ComparisonDetailMetric[]
  }
) => {
  const supplierKeys = quotes.map((q, idx) => quotationSupplierKey(q, idx))
  const rows: ComparisonRow[] = []

  const pushRow = (key: string, label: string, getter: (q: any) => number | null | undefined) => {
    const values: Record<string, any> = {}
    supplierKeys.forEach((name, idx) => {
      const v = getter(quotes[idx])
      values[name] = v != null && Number.isFinite(Number(v)) ? Number(v) : v ?? '-'
    })
    rows.push({ key, label, values, ...calcCompareStats(values) })
  }

  pushRow('material', '材料成本', (q) => sumMaterialCost(q))
  pushRow('process', '加工成本', (q) => sumProcessCost(q))
  pushRow('other', '其它成本', (q) => sumOtherCost(q))
  pushRow('overhead', '管销研费用', (q) => sumRfqField(q, 'total_opex_amt'))

  const profitValues: Record<string, any> = {}
  supplierKeys.forEach((name, idx) => {
    profitValues[name] = firstRfqField(quotes[idx], 'profit_rate') ?? '-'
  })
  rows.push({ key: 'profit', label: '利润', values: profitValues, ...calcCompareStats(profitValues) })

  const taxValues: Record<string, any> = {}
  supplierKeys.forEach((name, idx) => {
    const q = quotes[idx]
    const fromItem = firstRfqField(q, 'tax_rate')
    const fromProfit = (q.profit_costs || [])[0]?.tax_rate
    taxValues[name] = fromItem ?? fromProfit ?? '-'
  })
  rows.push({ key: 'tax', label: '税金', values: taxValues, ...calcCompareStats(taxValues) })

  const totalValues: Record<string, any> = {}
  supplierKeys.forEach((name, idx) => {
    const q = quotes[idx]
    const a = q.quote_amount
    if (a !== undefined && a !== null && a !== '') {
      const n = Number(a)
      totalValues[name] = Number.isFinite(n) ? n : a
    } else {
      const s = sumRfqField(q, 'total_price_incl_tax')
      totalValues[name] = s != null ? s : '-'
    }
  })
  rows.push({ key: 'total', label: '总价', values: totalValues, ...calcCompareStats(totalValues) })

  const rankValues = buildRanksByTotal(quotes, supplierKeys)
  rows.push({ key: 'rank', label: '报价排名', values: rankValues })

  /* 议价价格仅由杂采议价记录表回显（openComparison 中 merge），勿用报价明细 winning_bid_price 以免与议价记录不一致 */
  const bargainValues: Record<string, any> = {}
  supplierKeys.forEach((name) => {
    bargainValues[name] = ''
  })
  rows.push({
    key: 'bargain',
    label: '议价价格',
    values: bargainValues,
    avg: undefined,
    min: undefined
  })

  const winValues: Record<string, any> = {}
  supplierKeys.forEach((name, idx) => {
    const flag = quotes[idx]?.is_awarded ?? quotes[idx]?.isAwarded
    winValues[name] = flag === 1 || flag === true ? '是' : '否'
  })
  rows.push({ key: 'award', label: '中标否', values: winValues })

  const materialGroups = buildMaterialDetailGroups(quotes, supplierKeys, detailOpts?.materialMetrics)
  const processGroups = buildProcessDetailGroups(quotes, supplierKeys, detailOpts?.processMetrics)
  const otherDetails = buildOtherCostDetails(quotes, supplierKeys)

  const matRow = rows.find((r) => r.key === 'material')
  if (matRow && materialGroups.length) matRow.detailGroups = materialGroups
  const procRow = rows.find((r) => r.key === 'process')
  if (procRow && processGroups.length) procRow.detailGroups = processGroups
  const otherRow = rows.find((r) => r.key === 'other')
  if (otherRow && otherDetails.length) otherRow.details = otherDetails

  const suppliers = supplierKeys.map((name, idx) => ({
    name: name || `供应商${idx + 1}`,
    code: quotes[idx]?.supplier_code || quotes[idx]?.supplierCode || '',
    quotationId: quotes[idx]?.autoid ?? quotes[idx]?.id
  }))

  return { suppliers, rows }
}

/** 税率等：取首个非空值（接口 tax_rate / 嵌套 rfq_items、profit_costs） */
const firstNonEmptyString = (...vals: unknown[]) => {
  for (const v of vals) {
    if (v === null || v === undefined || v === '') continue
    const s = String(v).trim()
    if (s !== '') {
      const num = Number(s)
      if (isNaN(num)) {
        return s
      }
      return `${num.toFixed(2)}%`
    }
  }
  return ''
}

const openComparison = async (row: any) => {
  // const st = Number(row?.status)
  // if (![6, 7, 8].includes(st)) {
  //   ElMessage.warning('仅比议价中、价格审核或核价通过状态可查看比价')
  //   return
  // }
  comparisonDialog.currentRow = row
  expandedRowKeys.value = []
  comparisonDialog.visible = true
  comparisonDialog.loading = true
  comparisonDialog.title = `比价/议价 - ${row.title || row.inquiry_name || row.inquiry_no || ''}`
  const rfqFromRow = Array.isArray(row.rfq_items) ? row.rfq_items[0] : undefined
  const profitFromRow = Array.isArray(row.profit_costs)
    ? rfqFromRow?.part_id
      ? row.profit_costs.find((p: any) => p.part_id === rfqFromRow.part_id) || row.profit_costs[0]
      : row.profit_costs[0]
    : undefined
  comparisonDialog.baseInfo = {
    code: row.inquiry_no || '',
    partNo: String(row.part_no || row.part_id || rfqFromRow?.part_id || '').trim(),
    partName: String(row.part_name || rfqFromRow?.product_name || '').trim(),
    targetPrice: row.target_price != null ? String(row.target_price) : '',
    currency: String(row.currency || row.transaction_currency || '').trim(),
    taxRate: firstNonEmptyString(row.tax_rate, rfqFromRow?.tax_rate, profitFromRow?.tax_rate),
    dealPrice: row.win_price != null ? String(row.win_price) : '-',
    lowestProcessPrice: '-'
  }
  try {
    const listRes = await getQuotationList({ inquiry_no: row.inquiry_no, page: 1, page_size: 200 })
    const list = extractQuotationList(listRes)
    const details = await Promise.all(
      list.map((q: any) => getQuotationDetail(q.autoid ?? q.id))
    )
    const quotes = details.map((r: any) => unwrapQuotationDetail(r)).filter(Boolean)
    await ensureTemplatesLoaded()
    const tplCode = String(row?.template_code || row?.template || '').trim()
    let tplResolved: any = null
    if (tplCode) {
      tplResolved = templates.value.find((t: any) => t.template_no === tplCode) ?? null
      if (tplResolved) tplResolved = await fetchTemplateDetailIfNeeded(tplResolved)
    }
    let materialMetrics: ComparisonDetailMetric[] | undefined
    let processMetrics: ComparisonDetailMetric[] | undefined
    if (tplResolved) {
      const secs = normalizeSections(tplResolved.sections)
      const matSec = secs.find((s: any) => (s.title || s.name) === '材料成本')
      const procSec = secs.find((s: any) => (s.title || s.name) === '加工成本')
      if (matSec?.fields?.length) {
        const built = buildMaterialComparisonMetricsFromTemplateFields(matSec.fields)
        if (built.length) materialMetrics = built
      }
      if (procSec?.fields?.length) {
        const built = buildProcessComparisonMetricsFromTemplateFields(procSec.fields)
        if (built.length) processMetrics = built
      }
    }
    const { suppliers, rows } = buildComparisonRowsFromPisQuotes(quotes, { materialMetrics, processMetrics })
    comparisonDialog.quotes = quotes
    comparisonDialog.suppliers = suppliers
    comparisonDialog.rows = rows
    const rq0 = quotes[0]?.rfq_items?.[0]
    if (rq0) {
      if (!comparisonDialog.baseInfo.partNo) comparisonDialog.baseInfo.partNo = String(rq0.part_id || '').trim()
      if (!comparisonDialog.baseInfo.partName) comparisonDialog.baseInfo.partName = String(rq0.product_name || '').trim()
    }
    if (!comparisonDialog.baseInfo.taxRate) {
      const pcQ =
        quotes[0] && Array.isArray(quotes[0].profit_costs)
          ? rq0?.part_id
            ? quotes[0].profit_costs.find((p: any) => p.part_id === rq0.part_id) || quotes[0].profit_costs[0]
            : quotes[0].profit_costs[0]
          : undefined
      comparisonDialog.baseInfo.taxRate = firstNonEmptyString(rq0?.tax_rate, pcQ?.tax_rate)
    }
    if (!comparisonDialog.baseInfo.currency && quotes[0]) {
      const c = quotes[0].currency ?? quotes[0].transaction_currency
      if (c != null && c !== '') comparisonDialog.baseInfo.currency = String(c).trim()
    }
    try {
      const negRes = await api.GetNegotiationRecordsObj(row.id, {})
      const raw = negRes?.data?.data ?? negRes?.data
      const negList = Array.isArray(raw) ? raw : []
      mergeNegotiationIntoComparisonRows(rows, quotes, negList)
      if (negList.length) await applyComparisonRowsAfterNegotiationMerge(rows)
    } catch {
      /* 无议价记录时沿用报价单展示 */
    }
    /** 与表格「制程最低价」列一致：取「总价」行各供应商报价中的最小值，勿用「加工成本」或「议价价格」行 */
    const totalRow = rows.find((r) => r.key === 'total')
    if (totalRow && totalRow.min !== undefined) {
      comparisonDialog.baseInfo.lowestProcessPrice = String(totalRow.min)
    }
  } catch (e: any) {
    comparisonDialog.quotes = []
    comparisonDialog.suppliers = []
    comparisonDialog.rows = []
    ElMessage.error(e?.message || '加载比价信息失败')
  } finally {
    comparisonDialog.loading = false
  }
}

const updateComparisonRowStats = (row: any) => {
  if (row?.key === 'bargain') return
  const nums = Object.values(row.values || {})
    .map((v: any) => Number(v))
    .filter((v) => Number.isFinite(v)) as number[]
  if (nums.length) {
    row.avg = nums.reduce((a: number, b: number) => a + b, 0) / nums.length
    row.min = Math.min(...nums)
  } else {
    row.avg = undefined
    row.min = undefined
  }
}

const comparisonRowClassName = ({ row }: any) => {
  const has =
    (row.details && row.details.length) || (row.detailGroups && row.detailGroups.length)
  return has ? '' : 'no-expand'
}

const comparisonRowKeyFn = (row: ComparisonRow) => String(row.key || row.label || '')

const detailHeaderLabel = (row: ComparisonRow) => {
  if (row.key === 'material') return '材质'
  if (row.key === 'process') return '工站'
  if (row.key === 'other') return '类型'
  return '明细'
}

const handleComparisonExpandChange = (row: ComparisonRow, expandedRows: ComparisonRow[]) => {
  expandedRowKeys.value = expandedRows.map((r) => comparisonRowKeyFn(r))
}

const toggleCompareExpand = (row: ComparisonRow) => {
  const has =
    (row.details && row.details.length) || (row.detailGroups && row.detailGroups.length)
  if (!has) return
  const key = comparisonRowKeyFn(row)
  const next = !expandedRowKeys.value.includes(key)
  ;(compareTableRef.value as any)?.toggleRowExpansion?.(row, next)
  if (next) expandedRowKeys.value = [...expandedRowKeys.value, key]
  else expandedRowKeys.value = expandedRowKeys.value.filter((k) => k !== key)
}

const getComparisonRow = (key: string) => comparisonDialog.rows.find((r) => r.key === key)

const stripQuotationForPut = (q: any) => {
  if (!q || typeof q !== 'object') return q
  const { quote_amount, template_sections, inquiry_attachments, ...rest } = q
  return { ...rest }
}

const syncQuotesFromComparisonRows = () => {
  const awardRow = getComparisonRow('award')
  const keys = comparisonDialog.quotes.map((q, idx) => quotationSupplierKey(q, idx))
  return comparisonDialog.quotes.map((quote, idx) => {
    const key = keys[idx]
    const awarded = awardRow?.values?.[key] === '是'
    const next = stripQuotationForPut(quote) as any
    next.is_awarded = awarded ? 1 : 0
    const items = Array.isArray(next.rfq_items)
      ? next.rfq_items.map((it: any) => ({
          ...it,
          is_awarded: awarded ? 1 : 0,
          /* 议价后价格写入杂采议价记录表 bargaining_price，不使用上阶物料「中标价格」 */
          winning_bid_price: null
        }))
      : []
    next.rfq_items = items
    return next
  })
}

const validateComparisonAwardAndBargain = async () => {
  const keys = comparisonDialog.quotes.map((q, idx) => quotationSupplierKey(q, idx))
  const awardRow = getComparisonRow('award')
  const bargainRow = getComparisonRow('bargain')
  const awarded = keys.filter((k) => awardRow?.values?.[k] === '是')
  if (awarded.length === 0) {
    try {
      await ElMessageBox.confirm('当前比价未选择中标供应商，请确定是否流标？', '提示', {
        type: 'warning',
        confirmButtonText: '确定',
        cancelButtonText: '取消'
      })
    } catch {
      return false
    }
    return true
  }
  const missingBargain = awarded.some((k) => {
    const v = bargainRow?.values?.[k]
    if (v === undefined || v === null || v === '') return true
    const n = Number(v)
    return !Number.isFinite(n)
  })
  if (missingBargain) {
    ElMessage.warning('请先为中标供应商维护有效议价价格（数字）后再确认')
    return false
  }
  return true
}

const saveComparison = async (target: 'draft' | 'negotiated' | 'audit') => {
  const st = Number(comparisonDialog.currentRow?.status)
  if (target === 'negotiated' && ![5, 6].includes(st)) {
    ElMessage.warning('仅比议价中状态可确认比价')
    return
  }
  if (target === 'audit' && st !== 7) {
    ElMessage.warning('仅价格审核状态可提交核价')
    return
  }
  if (target !== 'draft' && !(await validateComparisonAwardAndBargain())) return

  const updates = syncQuotesFromComparisonRows()
  if (!updates.length) {
    ElMessage.warning('无可保存的报价数据')
    return
  }
  const keys = comparisonDialog.quotes.map((q, idx) => quotationSupplierKey(q, idx))
  const bargainRow = getComparisonRow('bargain')
  const awardRow = getComparisonRow('award')
  const pickQuotationItemTotals = (quote: any) => {
    const it = (quote.rfq_items || [])[0]
    if (!it) return { total_price_excl_tax: null as number | null, total_price_incl_tax: null as number | null }
    const ex = it.total_price_excl_tax
    const inc = it.total_price_incl_tax
    return {
      total_price_excl_tax: ex != null && ex !== '' && Number.isFinite(Number(ex)) ? Number(ex) : null,
      total_price_incl_tax: inc != null && inc !== '' && Number.isFinite(Number(inc)) ? Number(inc) : null
    }
  }
  const records = comparisonDialog.quotes
    .map((quote, idx) => {
      const key = keys[idx]
      const awarded = awardRow?.values?.[key] === '是'
      const bargRaw = bargainRow?.values?.[key]
      const bargNum = Number(bargRaw)
      const hasBarg = Number.isFinite(bargNum)
      const qn = String(quote.quotation_no || quote.quotationNo || '').trim()
      const totals = pickQuotationItemTotals(quote)
      return {
        quotation_no: qn,
        supplier_code: String(quote.supplier_code || quote.supplierCode || '').trim(),
        is_awarded: awarded ? 1 : 0,
        bargaining_price: hasBarg ? bargNum : null,
        total_price_excl_tax: totals.total_price_excl_tax,
        total_price_incl_tax: totals.total_price_incl_tax
      }
    })
    .filter((r) => r.quotation_no)
  if (!records.length) {
    ElMessage.warning('无可保存的议价记录（缺少报价单号）')
    return
  }

  comparisonDialog.loading = true
  try {
    await api.SaveNegotiationRecordsObj(comparisonDialog.currentRow.id, { records })
    try {
      const negRes = await api.GetNegotiationRecordsObj(comparisonDialog.currentRow.id, {})
      const raw = negRes?.data?.data ?? negRes?.data
      const negList = Array.isArray(raw) ? raw : []
      mergeNegotiationIntoComparisonRows(comparisonDialog.rows, comparisonDialog.quotes, negList)
      if (negList.length) await applyComparisonRowsAfterNegotiationMerge(comparisonDialog.rows)
    } catch {
      /* 回显失败时保留输入框当前值 */
    }
    await Promise.all(
      updates.map((q) => {
        const id = q.autoid ?? q.id
        if (!id) return Promise.resolve()
        return updateQuotation(id, stripQuotationForPut(q))
      })
    )
    if (target === 'negotiated') {
      await api.ConfirmNegotiationObj(comparisonDialog.currentRow.id)
      comparisonDialog.currentRow.status = 7
      ElMessage.success('已确认比价')
      crudExpose.doRefresh()
    } else if (target === 'audit') {
      await api.SubmitPriceAuditObj(comparisonDialog.currentRow.id)
      comparisonDialog.currentRow.status = 8
      ElMessage.success('已提交核价')
      crudExpose.doRefresh()
    } else {
      ElMessage.success('已暂存比价结果')
    }
  } catch (e: any) {
    ElMessage.error(formatRfqApiErrorMessage(e, '操作失败'))
  } finally {
    comparisonDialog.loading = false
  }
}

const onSaveComparisonDraft = () => saveComparison('draft')
const onConfirmComparison = () => saveComparison('negotiated')
const onSubmitComparisonReview = () => saveComparison('audit')

const toggleComparisonAward = (row: any, supName: string, val: boolean) => {
  if (!row.values) return
  row.values[supName] = val ? '是' : '否'
}

const removeVendor = (row: any) => {
  form.vendors = form.vendors.filter((v: any) => v !== row)
}

const addVendorRow = () => {
  form.vendors.push({
    id: Date.now(),
    name: '',
    supplier_id: '',
    supplier_code: '',
    supplier_name: '',
    contact: '',
    email: ''
  })
}

const addCostRow = (section: string) => {
  const newId = `r-${Date.now()}`
  costRows.value.push({ id: newId, section, field: newId, values: {} })
}

const removeCostRow = (row: CostRow) => {
  costRows.value = costRows.value.filter((r) => r !== row)
}

const onAttachmentChange = (type: 'drawing' | 'tender' | 'other', list: any[]) => {
  form.attachments[type] = list.map((item: any) => ({
    uid: item.uid,
    name: item.name,
    url: item.url || item.response?.url || '',
    raw: item.raw,
    status: item.status || 'ready'
  }))
}

const unwrapResponseData = (res: any) => res?.data?.data ?? res?.data ?? res

const uploadAttachmentFile = async (fileItem: any) => {
  if (fileItem?.url || fileItem?.file_path) {
    return {
      ...fileItem,
      url: fileItem.url || fileItem.file_path,
      file_path: fileItem.file_path || fileItem.url,
      status: 'ready'
    }
  }
  const rawFile = fileItem?.raw
  if (!rawFile) {
    return {
      ...fileItem,
      url: '',
      file_path: '',
      status: fileItem?.status || 'ready'
    }
  }
  const formData = new FormData()
  formData.append('file', rawFile)
  formData.append('upload_method', '1')
  const res = await api.UploadFile(formData)
  const uploaded = unwrapResponseData(res) || {}
  const filePath = uploaded.url || uploaded.file_url || ''
  return {
    ...fileItem,
    name: fileItem?.name || uploaded.name || rawFile.name || '',
    url: filePath,
    file_path: filePath,
    status: 'ready'
  }
}

const prepareAttachmentsForSubmit = async () => {
  const types: Array<'drawing' | 'tender' | 'other'> = ['drawing', 'tender', 'other']
  const entries = await Promise.all(
    types.map(async (type) => {
      const uploadedList = await Promise.all((form.attachments?.[type] || []).map((item: any) => uploadAttachmentFile(item)))
      return [type, uploadedList]
    })
  )
  return Object.fromEntries(entries) as typeof form.attachments
}

const loadCostItemsFromTemplate = async (tpl: any, force = false) => {
  const resolved = await fetchTemplateDetailIfNeeded(tpl)
  const rows = buildRowsFromTemplate(resolved)
  if (force || !costRows.value.length) {
    costRows.value = rows
  }
  sectionAddConfig.value = buildSectionAddConfig(resolved)
  applyPartNoToCostRows(form.part_no)
  applyTaxRateFromCurrency()
}

const sectionColumns = computed<Record<string, CostFieldColumn[]>>(() => {
  const res: Record<string, CostFieldColumn[]> = {}
  enabledSections.value.forEach((section) => {
    const map = new Map<string, CostFieldColumn>()
    const tplSec = templateSectionMap.value.get(section)
    if (tplSec && Array.isArray(tplSec.fields)) {
      tplSec.fields.forEach((f: any) => {
        if (f.key) {
          if (section === '加工成本' && f.key === 'process_fee') return
          if (partNoHiddenDisplaySections.has(section) && f.key === 'partNo') return
          map.set(f.key, {
            key: f.key,
            label: f.label || f.key,
            autoFill: Number(f.is_computed ?? f.isComputed ?? f.autoFill ?? 0) === 1 || f.autoFill === true,
            purchaserRequired:
              Number(f.purchaser_required ?? f.purchaserRequired ?? 0) === 1 || f.purchaserRequired === true,
            supplierRequiredCode: normalizeSupplierRequiredCode(f)
          })
        }
      })
    }
    costRows.value
      .filter((row) => row.section === section)
      .forEach((row) => {
        Object.keys(row.values || {}).forEach((k) => {
          if (section === '加工成本' && k === 'process_fee') return
          if (partNoHiddenDisplaySections.has(section) && k === 'partNo') return
          if (!map.has(k)) {
            map.set(k, {
              key: k,
              label: k,
              autoFill: isTemplateComputedField(section, k),
              purchaserRequired: templateFieldMetaMap.value.get(section)?.get(k)?.purchaserRequired === true
            })
          }
        })
      })
    res[section] = Array.from(map.values())
  })
  return res
})

const groupedCostRows = computed<Record<string, CostRow[]>>(() => {
  const map: Record<string, CostRow[]> = {}
  enabledSections.value.forEach((s) => {
    map[s] = []
  })
  costRows.value.forEach((r) => {
    const sec = r.section || '未分组'
    if (!enabledSections.value.includes(sec)) return
    if (!map[sec]) map[sec] = []
    map[sec].push(r)
  })
  return map
})

const fetchTemplates = async () => {
  templateLoading.value = true
  try {
    const res = await costTemplateApi.GetList({
      procurement_category: '2',
      acti: 'Y',
      status: 1,
      page: 1,
      pageSize: 200,
      page_size: 200
    })
    const list =
      res?.data?.results ||
      res?.data?.data ||
      res?.data?.list ||
      res?.results ||
      res?.list ||
      res?.data ||
      []
    templates.value = Array.isArray(list) ? list : []
    templatesLoaded.value = true
  } catch (e) {
    console.warn('加载询价模版失败', e)
    templates.value = []
    templatesLoaded.value = true
  } finally {
    templateLoading.value = false
  }
}

const ensureTemplatesLoaded = async () => {
  if (!templatesLoaded.value) {
    await fetchTemplates()
  }
}

watch(
  unitOptions,
  (options) => {
    if (!options.length) return
    stationOptions.value = stationOptions.value.map((station) => ({
      ...station,
      unit: normalizeUnitCode(station.unit)
    }))
    costRows.value.forEach((row) => {
      if (row.section !== '加工成本' || !row.values) return
      const unitKey = pickKey(row.values, processUnitKeys, 'unit')
      row.values[unitKey] = normalizeUnitCode(row.values[unitKey])
    })
  },
  { deep: true }
)

watch(
  () => form.template,
  async (val, oldVal) => {
    if (skipTemplateWatch.value) {
      skipTemplateWatch.value = false
      return
    }
    if (val && val !== oldVal) {
      let tpl = templates.value.find((t: any) => t.template_no === val)
      if (tpl) {
        tpl = await fetchTemplateDetailIfNeeded(tpl)
      }
      if (tpl) {
        applyTemplateMeta(tpl)
      }
      await loadCostItemsFromTemplate(tpl, true)
    }
  }
)

watch(
  () => form.currency,
  () => {
    applyTaxRateFromCurrency()
  }
)

watch(
  () => form.plant,
  (val, oldVal) => {
    if (val !== oldVal) {
      handlePlantChange(val)
    }
  }
)

watch(
  () => form.part_no,
  (val) => {
    applyPartNoToCostRows(val)
  }
)

const saveForm = async () => {
  if (isViewMode.value) return
  if (dialog.mode === 'edit' && !isOpenStatus(form.status)) {
    ElMessage.error('确认状态不允许编辑，请使用查看模式。')
    dialog.mode = 'view'
    return
  }
  if (!validatePurchaserRequiredFields()) return
  if (!validateQuoteDeadlineAfterOpenDay()) return
  if (!form.buyer && currentUserName.value) {
    form.buyer = currentUserName.value
  }
  if (dialog.mode === 'create') {
    form.purchase_dept = loginPurchaseDept()
  }
  const seenVendorKeys = new Set<string>()
  for (const v of form.vendors || []) {
    const k = vendorRowSelectKey(v)
    if (!k) continue
    if (seenVendorKeys.has(k)) {
      ElMessage.warning('供应商名单中存在重复供应商，请删除重复行或更换供应商后再保存')
      return
    }
    seenVendorKeys.add(k)
  }
  try {
    const uploadedAttachments = await prepareAttachmentsForSubmit()
    form.attachments = uploadedAttachments
    const partId = form.part_no || ''

    const buildMaterialCosts = () =>
      costRows.value
        .filter((r) => r.section === '材料成本')
        .map((r) => ({
          part_id: partId,
          material_spec: r.values?.material ?? r.values?.material_spec ?? '',
          length: r.values?.length ?? '',
          width: r.values?.width ?? '',
          height: r.values?.height ?? '',
          unit_price: r.values?.unitPrice ?? r.values?.unitprice ?? r.values?.unit_price ?? r.values?.price ?? null,
          qty: normalizeMaterialQtyForSubmit(
            r.values?.qty ?? r.values?.quantity ?? r.values?.num ?? r.values?.count
          ),
          specific_gravity: r.values?.specificgravity ?? r.values?.specific_gravity ?? '',
          material_cost: r.values?.material_cost ?? r.values?.materialCost ?? null,
          weight: (() => {
            const w = r.values?.weight ?? r.values?.Weight
            if (w === '' || w === null || w === undefined) return null
            const n = Number(w)
            return Number.isFinite(n) ? n : null
          })(),
          remark: r.values?.remark ?? '',
          option_json: JSON.stringify(r.values || {})
        }))

    const buildProcessCosts = () =>
      costRows.value
        .filter((r) => r.section === '加工成本')
        .map((r) => ({
          part_id: partId,
          process_station: r.values?.process_station ?? '',
          unit: normalizeUnitCode(r.values?.unit ?? r.values?.process_unit) || null,
          unit_rate: r.values?.unitrate ?? r.values?.unit_rate ?? null,
          process_qty: r.values?.processqty ?? r.values?.process_qty ?? '',
          process_price: r.values?.processprice ?? r.values?.process_price ?? null,
          remark: r.values?.remark ?? '',
          option_json: JSON.stringify(r.values || {})
        }))

    const otherRow = costRows.value.find((r) => r.section === '其它成本')?.values || {}
    const profitRow = costRows.value.find((r) => r.section === '利润')?.values || {}
    const taxRow = costRows.value.find((r) => r.section === '税金')?.values || {}
    const productDetailRow = costRows.value.find((r) => r.section === '产品明细')?.values || {}

    const packagingCost = Number(otherRow.packaging_cost ?? otherRow.packagingCost ?? 0) || 0
    const transportationCost = Number(otherRow.transportation_cost ?? otherRow.transportationCost ?? 0) || 0
    const profitRate = Number(profitRow.profitRate ?? profitRow.profit_rate ?? 0) || 0
    const taxRate = Number(taxRow.taxRate ?? taxRow.tax_rate ?? 0) || 0
    const targetPrice = Number(form.target_price) || 0
    const rfqPartId = String((productDetailRow.partNo ?? productDetailRow.part_id ?? partId) || '')
    const rfqProductName = (productDetailRow.desc ?? productDetailRow.product_name ?? form.part_name) || ''
    const rfqUnit = (productDetailRow.unit ?? form.part_unit) || ''
    const rfqQty = Number(productDetailRow.qty ?? productDetailRow.quantity ?? form.purchase_qty) || 0
    const rfqUnitPrice =
      Number(productDetailRow.price ?? productDetailRow.unitPrice ?? productDetailRow.unit_price ?? targetPrice) || 0

    const materialTotal = buildMaterialCosts().reduce((sum, r) => sum + (Number(r.material_cost) || 0), 0)
    const processTotal = buildProcessCosts().reduce((sum, r) => sum + (Number(r.process_price) || 0), 0)
    const otherTotal = packagingCost + transportationCost
    const exclTax = materialTotal + processTotal + otherTotal
    const inclTax = exclTax * (1 + taxRate)

    const payload: any = {
      inquiry_no: form.inquiry_no || undefined,
      title: form.title,
      purchase_type: 2,
      material_type: undefined,
      template: form.template_code || String(form.template || ''),
      is_bom: Number(form.is_bom) || 0,
      currency: form.currency,
      company_code: form.plant || undefined,
      purchase_dept: clipPurchaseDept(form.purchase_dept) || undefined,
      buyer: form.buyer,
      quote_deadline:
        Number(form.buying_method) === 1
          ? normalizeQuoteDeadline(form.quote_deadline) || undefined
          : null,
      buying_method: Number.isFinite(Number(form.buying_method)) ? Number(form.buying_method) : 1,
      bid_start_time:
        Number(form.buying_method) === 1
          ? null
          : normalizeDateTime(form.bid_start_time) || null,
      bid_end_time:
        Number(form.buying_method) === 1
          ? null
          : normalizeDateTime(form.bid_end_time) || null,
      target_price: targetPrice,
      lead_time_days: Number(form.lead_time_days) || 0,
      payment_method: Number(form.payment_method) || 1,
      status: Number(form.status) || STATUS_OPEN,
      remark: form.remark,
      suppliers: (form.vendors || []).map((v: any) => ({
        part_id: partId,
        supplier_code: v.supplier_code || v.supplier_id || v.name || '',
        supplier_name: v.supplier_name || v.name || '',
        contact_person: v.contact || '',
        contact_email: v.email || '',
        contact_phone: v.phone || ''
      })),
      attachments: ['drawing', 'tender', 'other'].flatMap((fileType: string) =>
        (uploadedAttachments?.[fileType] || []).map((f: any) => ({
          part_id: partId,
          file_type: attachmentTypeCodeMap[fileType as keyof typeof attachmentTypeCodeMap] || 3,
          file_name: f.name || f.file_name || '',
          file_path: f.url || f.file_path || '',
          upload_user: currentUserName.value || ''
        }))
      ),
      material_costs: buildMaterialCosts(),
      process_costs: buildProcessCosts(),
      other_costs: [
        {
          part_id: partId,
          packaging_cost: packagingCost,
          transportation_cost: transportationCost
        }
      ],
      profit_costs: [
        {
          part_id: partId,
          tax_rate: taxRate,
          profit_rate: profitRate
        }
      ],
      rfq_items: [
        {
          part_id: rfqPartId,
          product_name: rfqProductName,
          unit: rfqUnit,
          qty: rfqQty,
          is_bom: Number(form.is_bom) || 0,
          unit_price: rfqUnitPrice,
          total_material_cost: Number(materialTotal.toFixed(4)),
          total_processing_cost: Number(processTotal.toFixed(4)),
          total_other_expense: Number(otherTotal.toFixed(4)),
          total_opex_amt: 0,
          profit_rate: profitRate,
          total_price_excl_tax: Number(exclTax.toFixed(4)),
          tax_rate: taxRate,
          total_price_incl_tax: Number(inclTax.toFixed(4)),
          option_json: JSON.stringify(productDetailRow || {})
        }
      ]
    }
    if (dialog.mode === 'create') {
      await api.AddObj(payload)
    } else if (dialog.currentId) {
      await api.UpdateObj({ ...payload, id: dialog.currentId })
    }
    dialog.visible = false
    crudExpose.doRefresh()
  } catch (err: any) {
    ElMessage.error(getErrorMessage(err, '保存失败'))
  }
}

const { crudOptions } = createCrudOptions({
  crudExpose,
  onAdd: openCreate,
  onEdit: openEdit,
  onView: openView,
  onComparison: openComparison,
  onTableSelectionChange: (rows) => {
    selectedInquiryRows.value = rows || []
  },
  getTableSelection: () => selectedInquiryRows.value
})

useCrud({ crudExpose, crudOptions })

onMounted(() => {
  fetchTemplates()
  Promise.all([loadCompanyOptions(), loadPartOptions(), loadMaterialOptions(), loadSupplierOptions(), loadStationOptions(), loadUnitOptions()]).then(() => {
    if (companyOptions.value.length && !form.plant) {
      form.plant = companyOptions.value[0].value
      handlePlantChange(form.plant)
    }
  })
  crudExpose.doRefresh()
})
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 4px 12px;
}
.title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}
.sub {
  margin: 4px 0 0;
  color: #6b7280;
  font-size: 13px;
}
.actions {
  display: flex;
  gap: 8px;
}
.grid-form {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px 16px;
}
.grid-form :deep(.el-form-item) {
  margin-bottom: 0;
}
.grid-form .span2 {
  grid-column: span 2;
}
.grid-form .span3 {
  grid-column: span 3;
}
.grid-form .span4 {
  grid-column: span 4;
}
.quote-deadline-input {
  display: flex;
  gap: 8px;
  width: 100%;
}
.quote-deadline-input > :deep(*) {
  min-width: 0;
}
.dialog-body {
  min-height: 520px;
  display: flex;
  flex-direction: column;
}
.tabs-fill {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.tabs-fill :deep(.el-tabs__content) {
  flex: 1;
}
.tabs-fill :deep(.el-tab-pane) {
  min-height: 360px;
}
.attach-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}
.attach-block {
  padding: 12px;
  border: 1px dashed #d5d7de;
  border-radius: 6px;
  background: #fafafa;
}
.attach-title {
  margin-bottom: 8px;
  font-weight: 600;
  color: #374151;
}
.cost-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
  color: #4b5563;
}
.cost-groups {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.cost-group {
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 12px;
  background: #fff;
}
.cost-group-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}
.cost-row-pair {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
  gap: 12px;
}
.cost-sections {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.cost-section {
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 12px;
  background: #fff;
}
.cost-section-title {
  font-weight: 600;
  margin-bottom: 8px;
  color: #111827;
}
.cost-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 12px;
}
.cost-card {
  border-color: #eef2ff;
}
.cost-field {
  font-weight: 600;
  margin-bottom: 6px;
  color: #1f2937;
}
.cost-desc {
  --el-descriptions-border-color: #e5e7eb;
}

.compare-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.compare-info {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px 12px;
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: #fafafa;
}
.compare-info .info-item {
  display: flex;
  gap: 6px;
  color: #374151;
  font-size: 13px;
}
.compare-info .info-item .label {
  color: #6b7280;
}
.compare-table :deep(.is-min) {
  color: #0ea5e9;
  font-weight: 600;
}
.compare-table :deep(.no-expand .el-table__expand-icon) {
  visibility: hidden;
}
.compare-table :deep(.el-table__expanded-cell) {
  padding: 6px 12px;
  background: #f9fafb;
}
.compare-detail {
  padding: 4px 0 6px;
}
.compare-detail-group {
  margin-bottom: 12px;
}
.compare-detail-group:last-child {
  margin-bottom: 0;
}
.compare-detail-group-title {
  font-weight: 600;
  font-size: 13px;
  color: #065f46;
  background: linear-gradient(90deg, #d1fae5 0%, #ecfdf5 55%, transparent 100%);
  padding: 6px 10px;
  margin-bottom: 6px;
  border-radius: 4px;
  border-left: 3px solid #10b981;
}
.compare-detail-table {
  margin: 0;
}
.no-detail {
  color: #9ca3af;
  padding: 6px 0;
}
.expand-toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  margin-right: 6px;
  cursor: pointer;
  color: #374151;
  user-select: none;
  font-weight: 700;
}
.compare-table :deep(.hidden-expand .el-table__expand-icon) {
  opacity: 0;
  pointer-events: none;
}
.compare-table :deep(.el-table__header .hidden-expand .cell) {
  display: none;
}

.supplier-header-link {
  cursor: pointer;
  color: var(--el-color-primary);
  text-decoration: underline;
  text-underline-offset: 2px;
}
.supplier-header-link:hover {
  opacity: 0.85;
}

.quotation-preview-dialog .quote-preview-body {
  max-height: 72vh;
  overflow: auto;
}
.quote-preview-section {
  margin-bottom: 16px;
}
.quote-preview-section-title {
  font-weight: 600;
  font-size: 14px;
  color: #92400e;
  background: linear-gradient(90deg, #fde68a 0%, #fffbeb 50%, transparent 100%);
  padding: 8px 10px;
  margin-bottom: 8px;
  border-radius: 4px;
  border-left: 3px solid #f59e0b;
}
.quote-preview-total .quote-preview-total-value {
  font-size: 18px;
  font-weight: 700;
  color: #0f766e;
  padding: 8px 0;
}
</style>
