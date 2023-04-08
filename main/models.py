from django.db import models

# Create your models here.

class Imag(models.Model):
    img_id = models.AutoField(primary_key=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    class Meta:
        db_table = "imag"
