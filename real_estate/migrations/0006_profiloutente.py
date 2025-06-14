# Generated by Django 5.0.2 on 2025-05-22 08:05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('real_estate', '0005_praticaimmobiliare_completata'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfiloUtente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ruolo', models.CharField(choices=[('admin', 'Amministratore'), ('store_manager', 'Store Manager'), ('agente', 'Agente')], max_length=20)),
                ('filiale', models.CharField(max_length=100)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
