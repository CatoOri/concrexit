# Generated by Django 2.0.8 on 2018-11-14 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0008_2_refactor_documents'),
        ('events', '0031_auto_20181128_1950'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='documents',
            field=models.ManyToManyField(to='documents.Document', verbose_name='documents', blank=True),
        ),
    ]
