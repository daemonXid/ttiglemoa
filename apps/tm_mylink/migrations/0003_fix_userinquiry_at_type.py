# Generated manually to fix PostgreSQL type casting issue

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tm_mylink', '0002_inquiry_db_author'),
    ]

    operations = [
        # First, drop the problematic field
        migrations.RemoveField(
            model_name='inquiry_db',
            name='userinquiry_at',
        ),
        # Then, recreate it with the correct type
        migrations.AddField(
            model_name='inquiry_db',
            name='userinquiry_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='작성일'),
        ),
    ]