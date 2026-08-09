from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='comprobante',
            field=models.FileField(blank=True, null=True, upload_to='comprobantes/'),
        ),
    ]
