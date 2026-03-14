from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('skills', '0004_alter_skill_category'),  # ← CHANGE THIS to your LAST APPLIED migration name
    ]

    operations = [
        migrations.AddField(
            model_name='Skill',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]