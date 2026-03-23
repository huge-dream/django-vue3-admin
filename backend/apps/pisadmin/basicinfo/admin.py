# -*- coding: utf-8 -*-
from django.contrib import admin
from apps.pisadmin.basicinfo.models import (
    Unit, Currency, Supplier, Company
)


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ['unitname', 'unitcode', 'status']
    search_fields = ['unitname', 'unitcode']


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['currencyname', 'currencycode', 'factory', 'tax', 'status']
    search_fields = ['currencyname', 'currencycode']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['supplier_name', 'supplier_id', 'company_code', 'contact_person', 'status']
    search_fields = ['supplier_name', 'supplier_id', 'company_code']


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['company_code', 'company_name', 'company_short_name', 'status']
    search_fields = ['company_code', 'company_name']


