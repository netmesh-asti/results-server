# Generated by Django 4.1.1 on 2022-10-03 04:55

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_ntcspeedtest_region'),
    ]

    operations = [
        migrations.CreateModel(
            name='Barangays',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('psg_id', models.CharField(max_length=250)),
                ('name', models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lat', models.FloatField(default=0, validators=[django.core.validators.MaxValueValidator(90.0), django.core.validators.MinValueValidator(-90.0)])),
                ('lon', models.FloatField(default=0, validators=[django.core.validators.MaxValueValidator(180.0), django.core.validators.MinValueValidator(-180.0)])),
                ('region', models.CharField(default=None, max_length=255)),
                ('province', models.CharField(default=None, max_length=255)),
                ('municipality', models.CharField(default=None, max_length=255)),
                ('barangay', models.CharField(default=None, max_length=255)),
            ],
        ),
        migrations.RemoveField(
            model_name='ntcspeedtest',
            name='region',
        ),
        migrations.RemoveField(
            model_name='ntcspeedtest',
            name='test_device',
        ),
        migrations.AddField(
            model_name='mobileresult',
            name='test_device',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='core.mobiledevice'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mobileresult',
            name='tester',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ntcspeedtest',
            name='location',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='core.location'),
            preserve_default=False,
        ),
    ]
