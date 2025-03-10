# Generated by Django 5.1.3 on 2025-01-08 20:12

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_productionrecord"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Order",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "customer_type",
                    models.CharField(
                        choices=[
                            ("carpenter", "Carpintero"),
                            ("architect", "Arquitecto"),
                            ("customer", "Cliente Final"),
                        ],
                        max_length=20,
                        verbose_name="Tipo de Cliente",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pendiente"),
                            ("processing", "En Proceso"),
                            ("cutting", "En Corte"),
                            ("edge_banding", "En Enchapado"),
                            ("completed", "Completado"),
                            ("delivered", "Entregado"),
                        ],
                        default="pending",
                        max_length=20,
                        verbose_name="Estado",
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="orders/",
                        verbose_name="Imagen de Medidas",
                    ),
                ),
                ("notes", models.TextField(blank=True, verbose_name="Notas")),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Fecha de Creación"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Última Actualización"
                    ),
                ),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Cliente",
                    ),
                ),
            ],
            options={
                "verbose_name": "Pedido",
                "verbose_name_plural": "Pedidos",
                "ordering": ["-created_at"],
            },
        ),
    ]
