# Generated by Django 3.2.7 on 2022-08-04 09:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sightings', '0004_post_profile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sighting',
            name='description',
        ),
        migrations.RemoveField(
            model_name='sighting',
            name='duration',
        ),
        migrations.RemoveField(
            model_name='sighting',
            name='ufo_shape',
        ),
    ]
