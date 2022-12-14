# Generated by Django 4.1.4 on 2022-12-29 16:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0050_alter_employee_agency'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Agency',
            new_name='Office',
        ),
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_field_tester', models.BooleanField(default=True)),
                ('agent', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('office', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.office')),
            ],
        ),
        migrations.AlterField(
            model_name='ntcspeedtest',
            name='tester',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.agent'),
        ),
        migrations.AlterField(
            model_name='rfcdevice',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.agent'),
        ),
        migrations.DeleteModel(
            name='Employee',
        ),
    ]
