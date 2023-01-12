# Generated by Django 4.1.2 on 2022-10-13 07:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_alter_ntcregionaloffice_email_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ntcregionaloffice',
            options={'ordering': ['ntc_region'], 'verbose_name': 'NTC Regional Office', 'verbose_name_plural': 'Regional Offices'},
        ),
        migrations.RemoveConstraint(
            model_name='ntcregionaloffice',
            name='unique NRO details',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='date_created',
            new_name='registration',
        ),
        migrations.RemoveField(
            model_name='ntcregionaloffice',
            name='region',
        ),
        migrations.RemoveField(
            model_name='user',
            name='ntc_region',
        ),
        migrations.AddField(
            model_name='ntcregionaloffice',
            name='ntc_region',
            field=models.CharField(choices=[('1', 'Region I (Ilocos Region)'), ('2', 'Region II (Cagayan Valley)'), ('3', 'Region III (Central Luzon)'), ('4-A', 'Region IV-A (CALABARZON)'), ('4-B', 'Region IV-B MIMAROPA Region'), ('5', 'Region V (Bicol Region)'), ('6', 'Region VI (Western Visayas)'), ('7', 'Region VII (Central Visayas)'), ('8', 'Region VIII (Eastern Visayas)'), ('9', 'Region IX (Zamboanga Peninsula)'), ('10', 'Region X (Northern Mindanao)'), ('11', 'Region XI (Davao Region)'), ('12', 'Region XII (SOCCSKSARGEN)'), ('13', 'Region XIII (Caraga)'), ('NCR', 'National Capital Region (NCR)'), ('CAR', 'Cordillera Administrative Region (CAR)'), ('BARMM', 'Bangsamoro Autonomous Region In Muslim Mindanao (BARMM)'), ('Central', 'NTC Region Central'), ('unknown', 'Unknown')], default='unknown', max_length=20),
        ),
        migrations.AddField(
            model_name='user',
            name='nro',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='core.ntcregionaloffice'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='server',
            name='server_type',
            field=models.CharField(choices=[('local', 'Local'), ('overseas', 'Overseas'), ('ix', 'Internet Exchange'), ('web-based', 'Web-based'), ('rfc', 'RFC 6349'), ('unknown', 'Unknown')], default='unknown', max_length=20),
        ),
        migrations.AddConstraint(
            model_name='ntcregionaloffice',
            constraint=models.UniqueConstraint(fields=('ntc_region',), name='unique NRO details'),
        ),
    ]
