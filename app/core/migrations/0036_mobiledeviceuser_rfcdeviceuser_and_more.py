# Generated by Django 4.1.2 on 2022-10-25 09:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0035_alter_rfctest_options_remove_rfcresult_created_on'),
    ]

    operations = [
        migrations.CreateModel(
            name='MobileDeviceUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assigned_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='RfcDeviceUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assigned_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.RemoveConstraint(
            model_name='mobiledevice',
            name='unique mobile device',
        ),
        migrations.AddConstraint(
            model_name='mobiledevice',
            constraint=models.UniqueConstraint(fields=('user', 'serial_number', 'imei'), name='unique mobile device'),
        ),
        migrations.AddField(
            model_name='rfcdeviceuser',
            name='device',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.rfcdevice'),
        ),
        migrations.AddField(
            model_name='rfcdeviceuser',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='mobiledeviceuser',
            name='device',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.mobiledevice'),
        ),
        migrations.AddField(
            model_name='mobiledeviceuser',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddConstraint(
            model_name='rfcdeviceuser',
            constraint=models.UniqueConstraint(fields=('device', 'user'), name='One RFC device instance per user'),
        ),
        migrations.AddConstraint(
            model_name='mobiledeviceuser',
            constraint=models.UniqueConstraint(fields=('device', 'user'), name='One Mobile device instance per user'),
        ),
    ]
