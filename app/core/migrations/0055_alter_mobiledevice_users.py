# Generated by Django 4.1.4 on 2022-12-30 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0054_rfcdevice_unique-rfc-device'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mobiledevice',
            name='users',
            field=models.ManyToManyField(to='core.agent'),
        ),
    ]