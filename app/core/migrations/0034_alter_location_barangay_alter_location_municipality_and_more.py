# Generated by Django 4.1.2 on 2022-10-17 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0033_alter_location_barangay_alter_location_municipality_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='barangay',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='municipality',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='province',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='region',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
