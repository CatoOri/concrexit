# Generated by Django 2.1.4 on 2018-12-19 20:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0009_event_documents'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='eventdocument',
            options={'permissions': (('override_owner', 'Can access event document as if owner'),), 'verbose_name': 'event document', 'verbose_name_plural': 'event documents'},
        ),
    ]
