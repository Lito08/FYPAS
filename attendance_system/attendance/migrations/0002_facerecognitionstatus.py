# Generated by Django 5.1.5 on 2025-02-13 06:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0001_initial'),
        ('courses', '0010_alter_section_section_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='FaceRecognitionStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_enabled', models.BooleanField(default=False)),
                ('enabled_at', models.DateTimeField(blank=True, null=True)),
                ('section', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='courses.section')),
            ],
        ),
    ]
