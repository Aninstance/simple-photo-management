# Generated by Django 2.1.8 on 2019-04-17 16:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spm_app', '0006_auto_20190415_2301'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='photodata',
            name='spm_app_pho_file_na_a33cdf_idx',
        ),
    ]
