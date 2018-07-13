# Generated by Django 2.0 on 2018-07-12 16:30

from django.db import migrations


def insert_default_meeting_codes(apps, schema_editor):
    meeting_codes = {
        'C': 'CLOSED for Alcoholics & for those "with a desire to stop drinking."',  # noqa: E501
        'M': 'for Men Only',
        'W': 'for Women Only',
        'LGBT': 'Lesbian/Gay/Transgender/Bisexual',
        'BS': 'Babysitting Available',
        '*': 'Wheel Chair Access',
        '+': 'Signed for Hearing Impaired',
        'CF': 'Child Friendly',
    }
    MeetingCode = apps.get_model('aafinder', 'MeetingCode')
    for code, description in meeting_codes.items():
        MeetingCode.objects.get_or_create(code=code, description=description)


def delete_default_meeting_codes(apps, schema_editor):
    MeetingCode = apps.get_model('aafinder', 'MeetingCode')
    MeetingCode.objects.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('aafinder', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            insert_default_meeting_codes, delete_default_meeting_codes),
    ]