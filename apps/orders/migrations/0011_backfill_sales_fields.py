from django.db import migrations, models


def backfill_sales_fields(apps, schema_editor):
    Order = apps.get_model('orders', 'Order')
    User = apps.get_model('auth', 'User')
    staff_ids = User.objects.filter(is_staff=True).values_list('id', flat=True)
    Order.objects.filter(user_id__in=staff_ids).update(
        created_by=models.F('user'),
        customer_name='-',
    )


def dummy_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0010_order_created_by_order_customer_name'),
    ]

    operations = [
        migrations.RunPython(backfill_sales_fields, dummy_reverse),
    ]
