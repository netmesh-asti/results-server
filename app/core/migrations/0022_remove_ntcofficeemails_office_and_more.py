# Generated by Django 4.1.2 on 2022-10-12 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_ntcregionaloffice_email_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ntcofficeemails',
            name='office',
        ),
        migrations.RemoveField(
            model_name='ntcofficemob',
            name='office',
        ),
        migrations.RemoveField(
            model_name='ntcofficetele',
            name='office',
        ),
        migrations.AlterModelOptions(
            name='ntcregionaloffice',
            options={'ordering': ['region'], 'verbose_name': 'NTC Regional Office', 'verbose_name_plural': 'Regional Offices'},
        ),
        migrations.RemoveConstraint(
            model_name='ntcregionaloffice',
            name='unique NRO',
        ),
        migrations.AlterField(
            model_name='ntcregionaloffice',
            name='email',
            field=models.CharField(blank=True, default='test@example.com', help_text='Use , to separate multiple emails.', max_length=250),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='ntcregionaloffice',
            name='mission',
            field=models.CharField(blank=True, max_length=250),
        ),
        migrations.AlterField(
            model_name='ntcregionaloffice',
            name='mobile',
            field=models.CharField(blank=True, help_text='Use , to separate multiple Mobile No.', max_length=250),
        ),
        migrations.AlterField(
            model_name='ntcregionaloffice',
            name='telephone',
            field=models.CharField(blank=True, help_text='Use , to separate multiple Tele. No.', max_length=250),
        ),
        migrations.AlterField(
            model_name='ntcregionaloffice',
            name='vision',
            field=models.CharField(blank=True, max_length=250),
        ),
        migrations.AddConstraint(
            model_name='ntcregionaloffice',
            constraint=models.UniqueConstraint(fields=('region',), name='unique NRO details'),
        ),
        migrations.DeleteModel(
            name='NtcOfficeEmails',
        ),
        migrations.DeleteModel(
            name='NtcOfficeMob',
        ),
        migrations.DeleteModel(
            name='NtcOfficeTele',
        ),
    ]
