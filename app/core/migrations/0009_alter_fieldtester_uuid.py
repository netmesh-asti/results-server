# Generated by Django 4.0.6 on 2022-07-07 03:39

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_alter_fieldtester_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fieldtester',
            name='uuid',
            field=models.UUIDField(default=uuid.UUID('01b470a9-0434-4c3c-8e33-3c43cc78e100'), unique=True),
        ),
    ]
