# Generated by Django 2.0.8 on 2018-09-07 13:28

from django.db import migrations
import localflavor.generic.models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0023_auto_20180819_1542'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='bank_account',
            field=localflavor.generic.models.IBANField(blank=True, help_text='Bank account for direct debit', include_countries=('AT', 'BE', 'BG', 'CH', 'CY', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GB', 'GI', 'GR', 'HR', 'HU', 'IE', 'IS', 'IT', 'LI', 'LT', 'LU', 'LV', 'MC', 'MT', 'NL', 'NO', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK', 'SM'), max_length=34, null=True, use_nordea_extensions=False, verbose_name='Bank account'),
        ),
    ]
