# Generated by Django 5.2.2 on 2025-06-06 15:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_user_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='email',
        ),
    ]
