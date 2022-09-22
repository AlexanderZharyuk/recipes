# Generated by Django 4.1.1 on 2022-09-21 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_remove_favourites_recipe_recipe_favourite_in'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='favourite_in',
        ),
        migrations.AddField(
            model_name='recipe',
            name='favourite_in',
            field=models.ManyToManyField(blank=True, null=True, related_name='recipes', to='api.favourites', verbose_name='В избранном'),
        ),
    ]