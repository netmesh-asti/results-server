# Generated by Django 4.1.1 on 2022-09-15 01:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_ntcspeedtest_publicspeedtest_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ntcspeedtest',
            name='region',
            field=models.CharField(choices=[('1', 'Region I (Ilocos Region)'), ('2', 'Region II (Cagayan Valley)'), ('3', 'Region III (Central Luzon)'), ('4-A', 'Region IV-A (CALABARZON)'), ('4-B', 'Region IV-B MIMAROPA Region'), ('5', 'Region V (Bicol Region)'), ('6', 'Region VI (Western Visayas)'), ('7', 'Region VII (Central Visayas)'), ('8', 'Region VIII (Eastern Visayas)'), ('9', 'Region IX (Zamboanga Peninsula)'), ('10', 'Region X (Northern Mindanao)'), ('11', 'Region XI (Davao Region)'), ('12', 'Region XII (SOCCSKSARGEN)'), ('13', 'Region XIII (Caraga)'), ('NCR', 'National Capital Region (NCR)'), ('CAR', 'Cordillera Administrative Region (CAR)'), ('BARMM', 'Bangsamoro Autonomous Region In Muslim Mindanao (BARMM)'), ('Central', 'NTC Region Central'), ('unknown', 'Unknown')], default='unknown', max_length=20),
        ),
    ]
