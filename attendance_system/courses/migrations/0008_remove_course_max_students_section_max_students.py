# Generated by Django 5.1.5 on 2025-02-09 07:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0007_alter_course_max_students'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='max_students',
        ),
        migrations.AddField(
            model_name='section',
            name='max_students',
            field=models.PositiveIntegerField(default=30),
        ),
    ]
