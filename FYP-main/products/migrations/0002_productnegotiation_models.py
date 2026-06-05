from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductNegotiation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("open", "Open"), ("accepted", "Accepted"), ("rejected", "Rejected")], default="open", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("buyer", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="product_negotiations", to=settings.AUTH_USER_MODEL)),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="negotiations", to="products.product")),
            ],
            options={
                "ordering": ["-updated_at"],
                "unique_together": {("product", "buyer")},
            },
        ),
        migrations.CreateModel(
            name="ProductNegotiationOffer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("offer_price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("decision", models.CharField(choices=[("accept", "Accept"), ("reject", "Reject"), ("counter", "Counter")], max_length=20)),
                ("counter_price", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ("raw_ai_output", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("negotiation", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="offers", to="products.productnegotiation")),
            ],
            options={
                "ordering": ["created_at"],
            },
        ),
    ]
