# Generated by Django 4.0.2 on 2022-04-28 01:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='zgodba',
            name='ocena',
            field=models.IntegerField(default=0, verbose_name='Časovna ocena'),
        ),
    ]