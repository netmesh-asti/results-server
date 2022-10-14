# Generated by Django 4.1.2 on 2022-10-12 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_alter_ntcregionaloffice_email_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ntcregionaloffice',
            name='email',
            field=models.CharField(blank=True, help_text='Email Addresses separated by comma.', max_length=250),
        ),
        migrations.AlterField(
            model_name='ntcregionaloffice',
            name='mobile',
            field=models.CharField(blank=True, help_text='Mobile No. separated by comma.', max_length=250),
        ),
        migrations.AlterField(
            model_name='ntcregionaloffice',
            name='telephone',
            field=models.CharField(blank=True, help_text='Tel. No. separated by comma.', max_length=250),
        ),
    ]