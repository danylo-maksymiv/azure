

from django.db import migrations
import csv
import os
from decimal import Decimal

def load_addresses_from_csv(apps, schema_editor):
    Address = apps.get_model('blockchain', 'Address')
    csv_file_path = '/Users/cyp41k/Desktop/ПП/generated_addresses.csv'

    if not os.path.exists(csv_file_path):
        print(f"Файл {csv_file_path} не знайдено.")
        return

    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            Address.objects.update_or_create(
                address=row['address'],
                defaults={'eth_balance': Decimal(row['eth_balance'])}
            )

def remove_addresses_data(apps, schema_editor):
    Address = apps.get_model('blockchain', 'Address')
    csv_file_path = '/Users/cyp41k/Desktop/ПП/generated_addresses.csv'

    if not os.path.exists(csv_file_path):
        print(f"Файл {csv_file_path} не знайдено.")
        return

    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        addresses_to_delete = [row['address'] for row in reader]
        Address.objects.filter(address__in=addresses_to_delete).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('blockchain', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_addresses_from_csv, remove_addresses_data),
    ]


