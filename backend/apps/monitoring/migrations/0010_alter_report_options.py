# Generated by Django 3.2.4 on 2021-09-26 22:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monitoring', '0009_alter_report_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='report',
            options={'get_latest_by': 'order_date'},
        ),
    ]
