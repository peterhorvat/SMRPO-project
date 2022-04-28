# Generated by Django 4.0.2 on 2022-04-28 13:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0003_alter_sprint_koncni_cas_alter_sprint_zacetni_cas_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='belezenjecasa',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='belezenjecasa',
            name='sprint',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='website.sprint', verbose_name='Sprint'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='belezenjecasa',
            name='ure',
            field=models.IntegerField(default=0, verbose_name='Ure'),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='PastSprints',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sprint', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='website.sprint', verbose_name='Pretekli Sprint')),
                ('zgodba', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='website.zgodba', verbose_name='Zgodba')),
            ],
        ),
        migrations.RemoveField(
            model_name='belezenjecasa',
            name='konec',
        ),
    ]