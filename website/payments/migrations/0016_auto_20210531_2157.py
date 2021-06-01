# Generated by Django 3.2 on 2021-05-31 19:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0015_auto_20201017_1354'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='paymentuser',
            options={'verbose_name': 'payment user'},
        ),
        migrations.CreateModel(
            name='BlacklistedPaymentUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='payments.paymentuser')),
            ],
        ),
    ]
