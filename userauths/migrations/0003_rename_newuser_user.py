# Generated by Django 4.2.6 on 2024-02-16 04:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('admin', '0003_logentry_add_action_flag_choices'),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('userauths', '0002_rename_user_newuser'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='NewUser',
            new_name='User',
        ),
    ]
