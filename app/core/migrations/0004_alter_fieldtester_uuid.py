# Generated by Django 4.0.4 on 2022-05-13 06:32

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_fieldtester_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fieldtester',
            name='uuid',
            field=models.UUIDField(default=uuid.UUID('e5e687c6-7572-4f73-9637-976d1bdc5f12'), unique=True),
        ),
    ]
