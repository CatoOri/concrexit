# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-10-12 09:59
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def forward_func(apps, schema_editor):
    Order = apps.get_model('pizzas', 'Order')

    for order in Order.objects.all():
        if order.member:
            order.member_old = order.member
            order.save(update_fields=('member_old',))


class Migration(migrations.Migration):

    dependencies = [
        ('pizzas', '0003_0_user_foreign_keys'),
    ]

    operations = [
        migrations.RunPython(
            code=forward_func,
        ),
    ]
