from django.contrib import admin
from .models import Part, BOMFile, BOMEntry

@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ('mpn', 'manufacturer')
    search_fields = ('mpn', 'manufacturer')

@admin.register(BOMFile)
class BOMFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_master', 'uploaded_at')
    list_filter = ('user', 'is_master')
    search_fields = ('name',)

@admin.register(BOMEntry)
class BOMEntryAdmin(admin.ModelAdmin):
    list_display = ('part', 'bom_file', 'quantity', 'reference_designators')
    search_fields = ('part__mpn', 'part__manufacturer', 'bom_file__name')