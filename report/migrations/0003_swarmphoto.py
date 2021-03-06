# Generated by Django 3.0.6 on 2020-05-19 20:09

import cloudinary.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0002_swarmreport'),
    ]

    operations = [
        migrations.CreateModel(
            name='SwarmPhoto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('image', cloudinary.models.CloudinaryField(max_length=255, verbose_name='image')),
                ('swarm', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, to='report.SwarmReport')),
            ],
        ),
    ]
