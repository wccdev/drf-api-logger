# Generated by Django 3.2.12 on 2022-04-19 02:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drf_api_logger', '0006_auto_20220419_1002'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apilogsmodel',
            name='body',
            field=models.JSONField(null=True),
        ),
    ]
