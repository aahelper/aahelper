# Generated by Django 2.0.7 on 2018-07-17 15:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aafinder', '0005_populate_slug_field'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='meetingtype',
            name='is_day_of_week',
        ),
    ]
