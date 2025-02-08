# Generated by Django 5.1.5 on 2025-02-08 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='first_login',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='personal_email',
            field=models.EmailField(blank=True, default='default@example.com', max_length=254, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(default='default@university.com', max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(default='default', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(default='Last', max_length=50),
            preserve_default=False,
        ),
    ]
