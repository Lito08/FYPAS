# Generated by Django 5.1.5 on 2025-02-13 16:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0010_alter_section_section_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='section',
            name='schedule',
        ),
        migrations.AddField(
            model_name='section',
            name='class_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='section',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='ClassSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('week_number', models.IntegerField()),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sessions', to='courses.section')),
            ],
        ),
    ]
