# Generated by Django 4.0.7 on 2022-08-04 10:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_rename_serialnumber_rfcdevice_serial_number'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='rfcdevice',
            name='unique rfc device',
        ),
        migrations.AddField(
            model_name='rfcdevice',
            name='name',
            field=models.CharField(blank=True, max_length=250),
        ),
        migrations.AddConstraint(
            model_name='rfcdevice',
            constraint=models.UniqueConstraint(fields=('user', 'serial_number'), name='unique rfc device'),
        ),
    ]
