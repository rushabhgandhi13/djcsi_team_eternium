from django.contrib import admin

# Register your models here.
from .models import Imag

@admin.register(Imag)
class ImagAdmin(admin.ModelAdmin):
	list_display = ("img_id", "image")