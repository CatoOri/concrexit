# Generated by Django 3.1.1 on 2020-09-07 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pushnotifications', '0017_sent_date_complete'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='description_nl',
        ),
        migrations.RemoveField(
            model_name='category',
            name='name_nl',
        ),
        migrations.RemoveField(
            model_name='message',
            name='body_nl',
        ),
        migrations.RemoveField(
            model_name='message',
            name='title_nl',
        ),
        migrations.AlterField(
            model_name='device',
            name='language',
            field=models.CharField(choices=[('en', 'English')], default='en', max_length=2, verbose_name='language'),
        ),
    ]
