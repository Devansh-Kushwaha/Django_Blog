# Generated by Django 5.0.6 on 2024-06-23 08:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_rename_title_blogpost_title'),
    ]

    operations = [
        migrations.RenameField(
            model_name='blogpost',
            old_name='thumbail',
            new_name='thumbnail',
        ),
    ]
