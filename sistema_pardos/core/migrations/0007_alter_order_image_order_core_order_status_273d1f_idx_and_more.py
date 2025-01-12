# Generated by Django 5.1.3 on 2025-01-12 16:31

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_orderstatushistory_stockalert"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="image",
            field=models.ImageField(
                blank=True,
                help_text="Imagen opcional del proyecto o espacio (plano, boceto o fotografía)",
                null=True,
                upload_to="orders/%Y/%m/",
                verbose_name="Imagen de Referencia",
            ),
        ),
        migrations.AddIndex(
            model_name="order",
            index=models.Index(
                fields=["status", "created_at"], name="core_order_status_273d1f_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="order",
            index=models.Index(
                fields=["customer", "-created_at"], name="core_order_custome_fdf03b_idx"
            ),
        ),
    ]
