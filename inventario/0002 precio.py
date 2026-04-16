from django.db import migrations, models
 
 
class Migration(migrations.Migration):
 
    dependencies = [
        ('inventario', '0001_initial'),
    ]
 
    operations = [
        migrations.AddField(
            model_name='producto',
            name='precio_unitario',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=12,
                verbose_name='Precio unitario',
            ),
        ),
    ]
 