# Generated by Django 4.0.6 on 2022-07-20 02:57

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_rfcresult_gps_lon'),
    ]

    operations = [
        migrations.AddField(
            model_name='mobileresult',
            name='test_id',
            field=models.UUIDField(blank=True, default=uuid.uuid4, editable=False, null=True, unique=True),
        ),
    ]
