from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("sellers", "0005_remove_orderitem_order_alter_message_order_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="sellerprofile",
            name="is_verified",
        ),
    ]
