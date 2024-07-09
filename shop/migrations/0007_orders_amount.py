from django.db import migrations, models

def set_default_amount(apps, schema_editor):
    Orders = apps.get_model('shop', 'Orders')
    for order in Orders.objects.all():
        if order.amount is None:  # Adjust the condition based on your data
            order.amount = 0  # Set your default value here
            order.save()

class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0006_orderupdate'),  # Update to the correct previous migration
    ]

    operations = [
        migrations.AddField(
            model_name='orders',
            name='amount',
            field=models.IntegerField(default=0),
        ),
        migrations.RunPython(set_default_amount),
    ]
