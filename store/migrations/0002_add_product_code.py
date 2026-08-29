from django.db import migrations, models
import uuid


def generate_codes(apps, schema_editor):
    Product = apps.get_model('store', 'Product')
    for p in Product.objects.all():
        if not getattr(p, 'product_code', None):
            p.product_code = f"SOR-{uuid.uuid4().hex[:8].upper()}"
            p.save(update_fields=['product_code'])


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='product_code',
            field=models.CharField(
                blank=True,
                help_text='Auto-generated unique code (e.g. SOR-A1B2C3D4)',
                max_length=20,
                null=True,
                unique=True,
                verbose_name='Product Code',
            ),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='product_code',
            field=models.CharField(
                blank=True,
                default='',
                max_length=20,
                verbose_name='Product Code',
            ),
        ),
        migrations.RunPython(generate_codes, migrations.RunPython.noop),
    ]
