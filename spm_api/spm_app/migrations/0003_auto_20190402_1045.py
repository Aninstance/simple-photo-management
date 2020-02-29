# Generated by Django 2.1.8 on 2019-04-02 10:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spm_app', '0002_auto_20190401_1745'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='photodata',
            name='tags',
        ),
        migrations.AddField(
            model_name='phototag',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='photo_tag', to='spm_app.PhotoData'),
        ),
    ]