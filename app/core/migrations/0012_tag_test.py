# Generated by Django 4.0.8 on 2022-12-08 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_alter_project_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='test',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
