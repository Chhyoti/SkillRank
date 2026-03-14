from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('skills', '0005_add_missing_description'),  # latest migration
        ('users', '__first__'),  # assumes Profile model exists in users app
    ]

    operations = [
        migrations.CreateModel(
            name='UserSkill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),

                ('proficiency', models.PositiveSmallIntegerField(
                    choices=[
                        (1, 'Beginner'),
                        (2, 'Elementary'),
                        (3, 'Intermediate'),
                        (4, 'Advanced'),
                        (5, 'Expert')
                    ],
                    default=3
                )),

                ('added_at', models.DateTimeField(auto_now_add=True)),

                ('profile', models.ForeignKey(
                    on_delete=models.CASCADE,
                    related_name='user_skills',
                    to='users.profile'
                )),

                ('skill', models.ForeignKey(
                    on_delete=models.CASCADE,
                    to='skills.skill'
                )),
            ],

            options={
                'unique_together': {('profile', 'skill')},
                'ordering': ['skill__name'],
            },
        ),
    ]