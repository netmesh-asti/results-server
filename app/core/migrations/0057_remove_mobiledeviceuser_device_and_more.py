# Generated by Django 4.1.4 on 2023-01-05 18:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0056_alter_rfctest_tester'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mobiledeviceuser',
            name='device',
        ),
        migrations.RemoveField(
            model_name='mobiledeviceuser',
            name='user',
        ),
        migrations.DeleteModel(
            name='ActivatedMobDevice',
        ),
        migrations.DeleteModel(
            name='MobileDeviceUser',
        ),
    ]