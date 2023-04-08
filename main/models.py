from django.db import models

# Create your models here.

class Imag(models.Model):
    img_id = models.AutoField(primary_key=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    class Meta:
        db_table = "imag"

class Point(models.Model):
    img_id = models.ForeignKey(Imag, on_delete=models.CASCADE, null=True, blank=True)
    x = models.IntegerField()
    y = models.IntegerField()
    class Meta:
        db_table = "points"