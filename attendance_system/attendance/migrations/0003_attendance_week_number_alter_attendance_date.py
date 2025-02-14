# Generated by Django 5.1.5 on 2025-02-13 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0002_facerecognitionstatus'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='week_number',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='date',
            field=models.DateField(),
        ),
    ]
