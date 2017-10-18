# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-10-12 10:28
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


def forward_func(apps, schema_editor):
    MailingList = apps.get_model('mailinglists', 'MailingList')

    for mailinglist in MailingList.objects.all():
        for member in mailinglist.members.all():
            mailinglist.members_old.add(member)


class Migration(migrations.Migration):

    dependencies = [
        ('mailinglists', '0010_0_user_foreign_keys'),
    ]

    operations = [
        migrations.RunPython(
            code=forward_func,
        ),
    ]
