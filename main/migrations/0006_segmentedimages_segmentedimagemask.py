# Generated by Django 4.2 on 2023-04-10 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_suggestions'),
    ]

    operations = [
        migrations.AddField(
            model_name='segmentedimages',
            name='segmentedImageMask',
            field=models.ImageField(blank=True, null=True, upload_to='images/mask/'),
        ),
    ]
