# Generated by Django 3.2.7 on 2024-08-14 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_task'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='call_room_id',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
    ]
