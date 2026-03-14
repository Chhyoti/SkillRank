from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('skills', '0002_skill_created_at'),  # ← must point to the last applied migration
    ]

    operations = [
        migrations.AddField(
            model_name='Skill',
            name='category',
            field=models.CharField(max_length=80, blank=True),
        ),
    ]