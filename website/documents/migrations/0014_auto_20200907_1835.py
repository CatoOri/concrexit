# Generated by Django 3.1.1 on 2020-09-07 16:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0013_auto_20200125_1748'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='file_nl',
        ),
        migrations.RemoveField(
            model_name='document',
            name='name_nl',
        ),
        migrations.RemoveField(
            model_name='generalmeeting',
            name='location_nl',
        ),
    ]
