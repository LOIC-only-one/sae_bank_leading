# Generated by Django 5.2.3 on 2025-06-18 09:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('logging_api', '0008_logstatus'),
    ]

    operations = [
        migrations.DeleteModel(
            name='LogStatus',
        ),
    ]
