# Generated by Django 5.1.7 on 2025-03-14 08:07

import apps.address_registry.models
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Gyvenviete',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isregistruota', models.DateField()),
                ('registruota', models.DateField()),
                ('pavadinimas', models.CharField(max_length=255)),
                ('kurortas', models.BooleanField()),
                ('plotas', models.FloatField()),
                ('tipas', models.CharField(choices=apps.address_registry.models.get_vietoves_tipai)),
            ],
            options={
                'verbose_name': 'Gyvenviete',
                'verbose_name_plural': 'Gyvenvietes',
            },
        ),
        migrations.CreateModel(
            name='Pavadinimas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pavadinimas', models.CharField(max_length=255)),
                ('kirciuotas', models.CharField(max_length=255)),
                ('linksnis', models.CharField(choices=apps.address_registry.models.get_linksniai, max_length=255)),
                ('gyvenviete', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pavadinimo_formos', to='address_registry.gyvenviete')),
            ],
            options={
                'verbose_name': 'Pavadinimas',
                'verbose_name_plural': 'Pavadinimai',
            },
        ),
    ]
