# Generated by Django 3.2.7 on 2024-08-08 02:46

from django.db import migrations, models
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_user_avatar'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={},
        ),
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('object', django.db.models.manager.Manager()),
            ],
        ),
        migrations.RemoveField(
            model_name='user',
            name='date_joined',
        ),
        migrations.RemoveField(
            model_name='user',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='user',
            name='groups',
        ),
        migrations.RemoveField(
            model_name='user',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='user',
            name='is_staff',
        ),
        migrations.RemoveField(
            model_name='user',
            name='last_name',
        ),
        migrations.RemoveField(
            model_name='user',
            name='user_permissions',
        ),
        migrations.AddField(
            model_name='user',
            name='birth_date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='status',
            field=models.CharField(choices=[('online', 'on_line'), ('offline', 'off_line')], default='offline', max_length=50),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_superuser',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
