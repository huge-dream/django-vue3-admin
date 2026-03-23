# -*- coding: utf-8 -*-
from django.contrib import admin

from apps.pisadmin.miscprocurement.models import (
    MiscProcMaterial,
    MiscProcurementMaterialInfo,
    MiscProcurementStationInfo,
)


@admin.register(MiscProcurementMaterialInfo)
class MiscProcurementMaterialInfoAdmin(admin.ModelAdmin):
    list_display = ["materialtype", "factory", "density", "price", "status"]
    search_fields = ["materialtype", "factory"]


@admin.register(MiscProcurementStationInfo)
class MiscProcurementStationInfoAdmin(admin.ModelAdmin):
    list_display = ["stationname", "stationcode", "company_code", "stationtype", "rate", "status"]
    search_fields = ["stationname", "stationcode", "company_code"]


@admin.register(MiscProcMaterial)
class MiscProcMaterialAdmin(admin.ModelAdmin):
    list_display = ["partid", "partid_name", "company_code", "status"]
    search_fields = ["partid", "partid_name", "company_code"]
