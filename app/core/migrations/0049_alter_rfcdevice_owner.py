# Generated by Django 4.1.4 on 2022-12-28 17:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0048_alter_ntcspeedtest_tester'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rfcdevice',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.employee'),
        ),
    ]
