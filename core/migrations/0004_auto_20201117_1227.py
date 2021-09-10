# Generated by Django 2.2.14 on 2020-11-17 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20201117_1210'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='category',
            field=models.CharField(choices=[('Shirt', 'Shirt'), ('Sportwear', 'Sportwear'), ('Outwear', 'Outwear')], max_length=2),
        ),
        migrations.AlterField(
            model_name='item',
            name='label',
            field=models.CharField(choices=[('primary', 'primary'), ('secondary', 'secondary'), ('danger', 'danger')], max_length=1),
        ),
    ]
