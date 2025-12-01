from django.contrib import admin
from .models import BOMItem

@admin.register(BOMItem)
class BOMItemAdmin(admin.ModelAdmin):
    list_display = ('reference_designators', 'quantity', 'identified_mpn', 'identified_manufacturer')
    search_fields = ('reference_designators', 'identified_mpn', 'identified_manufacturer')
