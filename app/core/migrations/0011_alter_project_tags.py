# Generated by Django 4.0.8 on 2022-12-08 07:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_alter_milestone_description_alter_milestone_parent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='projects', to='core.tag'),
        ),
    ]
