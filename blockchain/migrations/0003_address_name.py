# Generated by Django 4.2.16 on 2024-12-13 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blockchain', '0002_load_addresses_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='name',
            field=models.CharField(default='', max_length=40),
        ),
    ]
