from django.contrib import admin

# Register your models here.
from .models import Imag, Point, SegmentedImages, Suggestions

@admin.register(Imag)
class ImagAdmin(admin.ModelAdmin):
	list_display = ("img_id", "image")


@admin.register(Point)
class PointAdmin(admin.ModelAdmin):
	list_display = ("id", "x", "y")

@admin.register(SegmentedImages)
class SegmentedImagesAdmin(admin.ModelAdmin):
	list_display = ("segImg_id", "segmentedImage")
 
@admin.register(Suggestions)
class SegmentedImagesAdmin(admin.ModelAdmin):
	list_display = ("sugImg_id", "sugImage")