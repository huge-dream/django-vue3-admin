# -*- coding: utf-8 -*-
from django.contrib import admin
from sscadmin.basicinfo.models import (
    Unit, Currency, MiscProcurementMaterialInfo, MiscProcurementStationInfo,
    Supplier, Company, MiscProcMaterial
)


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ['unitname', 'unitcode', 'status']
    search_fields = ['unitname', 'unitcode']


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['currencyname', 'currencycode', 'factory', 'tax', 'status']
    search_fields = ['currencyname', 'currencycode']


@admin.register(MiscProcurementMaterialInfo)
class MiscProcurementMaterialInfoAdmin(admin.ModelAdmin):
    list_display = ['materialtype', 'factory', 'density', 'price', 'status']
    search_fields = ['materialtype', 'factory']


@admin.register(MiscProcurementStationInfo)
class MiscProcurementStationInfoAdmin(admin.ModelAdmin):
    list_display = ['stationname', 'stationcode', 'company_code', 'stationtype', 'rate', 'status']
    search_fields = ['stationname', 'stationcode', 'company_code']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['supplier_name', 'supplier_id', 'company_code', 'contact_person', 'status']
    search_fields = ['supplier_name', 'supplier_id', 'company_code']


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['company_code', 'company_name', 'company_short_name', 'status']
    search_fields = ['company_code', 'company_name']


@admin.register(MiscProcMaterial)
class MiscProcMaterialAdmin(admin.ModelAdmin):
    list_display = ['partid', 'partid_name', 'company_code', 'status']
    search_fields = ['partid', 'partid_name', 'company_code']
