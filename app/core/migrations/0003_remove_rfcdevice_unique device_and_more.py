# Generated by Django 4.0.6 on 2022-08-02 03:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_mobiledevice_client_rfcdevice_client'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='rfcdevice',
            name='unique device',
        ),
        migrations.AddConstraint(
            model_name='mobiledevice',
            constraint=models.UniqueConstraint(fields=('user', 'serial_number'), name='unique mobile device'),
        ),
        migrations.AddConstraint(
            model_name='mobileresult',
            constraint=models.UniqueConstraint(fields=('timestamp', 'test_device'), name='unique mobile results'),
        ),
        migrations.AddConstraint(
            model_name='rfcdevice',
            constraint=models.UniqueConstraint(fields=('user', 'serialnumber'), name='unique rfc device'),
        ),
    ]
