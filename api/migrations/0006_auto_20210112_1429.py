# Generated by Django 3.0.8 on 2021-01-12 05:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20210111_1902'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='image2',
            field=models.ImageField(blank=True, null=True, upload_to='media'),
        ),
        migrations.AlterField(
            model_name='course',
            name='image3',
            field=models.ImageField(blank=True, null=True, upload_to='media'),
        ),
    ]
