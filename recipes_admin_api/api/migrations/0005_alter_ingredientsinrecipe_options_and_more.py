# Generated by Django 4.1.1 on 2022-09-21 11:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_ingredientsinrecipe_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingredientsinrecipe',
            options={'verbose_name': 'ингредиент', 'verbose_name_plural': 'ингредиенты'},
        ),
        migrations.AlterField(
            model_name='ingredientsinrecipe',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to='api.ingredient', verbose_name='Ингредиенты в рецепте'),
        ),
    ]
