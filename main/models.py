from django.db import models

# Create your models here.

class Imag(models.Model):
    img_id = models.AutoField(primary_key=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    class Meta:
        db_table = "imag"

class Point(models.Model):
    img_id = models.ForeignKey(Imag, on_delete=models.CASCADE, null=True, blank=True)
    color = models.CharField(max_length=20, null=True, blank=True)
    x = models.IntegerField()
    y = models.IntegerField()
    class Meta:
        db_table = "points"
    
class SegmentedImages(models.Model):
    segImg_id = models.ForeignKey(Imag, on_delete=models.CASCADE, null=True, blank=True)
    segmentedImage = models.ImageField(upload_to='images/results/', null=True, blank=True)
    segmentedImageMask = models.CharField(max_length=50000, default="")
    class Meta:
        db_table = "segmented_images"
        
class Suggestions(models.Model):
    sugImg_id = models.ForeignKey(Imag, on_delete=models.CASCADE, null=True, blank=True)
    sugImage = models.ImageField(upload_to='images/suggestions/', null=True, blank=True)
    class Meta:
        db_table = "suggested_images"