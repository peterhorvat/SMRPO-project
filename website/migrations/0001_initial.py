# Generated by Django 4.0.2 on 2022-04-21 17:04

import autoslug.fields
import ckeditor.fields
from django.conf import settings
import django.contrib.auth.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Uporabnik',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('username', models.CharField(max_length=30, unique=True, verbose_name='Uporabniško ime')),
                ('first_name', models.CharField(max_length=30, verbose_name='Ime')),
                ('last_name', models.CharField(max_length=150, verbose_name='Priimek')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='e-mail')),
                ('slug', autoslug.fields.AutoSlugField(blank=True, default='', editable=False, max_length=255, null=True, populate_from='username', verbose_name='Username slug')),
                ('otp_auth', models.BooleanField(default=True, verbose_name='Zahtevana OTP avtentikacija')),
                ('previous_login', models.DateTimeField(blank=True, null=True, verbose_name='Prejšnja prijava')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Uporabnik',
                'verbose_name_plural': 'Uporabniki',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Besedila',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tekst', ckeditor.fields.RichTextField(verbose_name='Vsebina besedila')),
                ('naslov', models.CharField(max_length=50, verbose_name='Naslov besedila')),
                ('uporaba', models.CharField(help_text='Kje točno se uporablja besedilo', max_length=255, verbose_name='Uporaba besedila')),
                ('slug', autoslug.fields.AutoSlugField(default='', editable=False, max_length=255, populate_from='naslov', verbose_name='Slug Besedila')),
            ],
            options={
                'verbose_name': 'Privezo besedilo',
                'verbose_name_plural': 'Privzeta besedila',
            },
        ),
        migrations.CreateModel(
            name='Clan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Član',
                'verbose_name_plural': 'Člani',
            },
        ),
        migrations.CreateModel(
            name='Projekt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ime', models.CharField(max_length=255, verbose_name='Ime projekta')),
                ('opis', models.TextField(default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Projekt',
                'verbose_name_plural': 'Projekti',
            },
        ),
        migrations.CreateModel(
            name='Sprint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ime', models.CharField(blank=True, max_length=255, null=True, verbose_name='Ime sprinta')),
                ('zacetni_cas', models.DateTimeField(verbose_name='Začetni čas sprinta')),
                ('koncni_cas', models.DateTimeField(verbose_name='Končni čas sprinta')),
                ('hitrost', models.IntegerField(verbose_name='Predvidena hitrost sprinta')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('projekt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.projekt', verbose_name='Projekt')),
            ],
            options={
                'verbose_name': 'Sprint',
                'verbose_name_plural': 'Sprinti',
            },
        ),
        migrations.CreateModel(
            name='Zgodba',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ime', models.CharField(max_length=255, verbose_name='Ime zgodbe')),
                ('vsebina', ckeditor.fields.RichTextField(verbose_name='Vsebina zgodbe')),
                ('sprejemni_testi', ckeditor.fields.RichTextField(verbose_name='Sprejemni testi zgodbe')),
                ('poslovna_vrednost', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)], verbose_name='Poslovna vrednost zgodbe')),
                ('prioriteta', models.IntegerField(choices=[(3, 'Could have'), (2, 'Should have'), (1, 'Must have'), (-1, "Won't have this time")], verbose_name='Prioriteta')),
                ('opombe', ckeditor.fields.RichTextField(verbose_name='Opombe zgodbe')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('projekt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.projekt', verbose_name='Projekt')),
                ('sprint', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='website.sprint', verbose_name='Sprint')),
            ],
            options={
                'verbose_name': 'Zgodba',
                'verbose_name_plural': 'Zgodbe',
            },
        ),
        migrations.CreateModel(
            name='Objava',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('naslov', models.CharField(blank=True, max_length=255, null=True, verbose_name='Naslov objave')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('clan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.clan', verbose_name='Član')),
            ],
            options={
                'verbose_name': 'Objava',
                'verbose_name_plural': 'Objave',
            },
        ),
        migrations.CreateModel(
            name='Naloga',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ime', models.CharField(blank=True, max_length=255, null=True, verbose_name='Ime naloge')),
                ('opis', ckeditor.fields.RichTextField(verbose_name='Opis naloge')),
                ('cas', models.IntegerField(verbose_name='Ocena časa')),
                ('status', models.IntegerField(choices=[(-1, 'Nedodeljena'), (0, 'Dodeljena'), (1, 'Aktivna'), (2, 'Zaključena')], verbose_name='Status naloge')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('clan', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='website.clan', verbose_name='Član')),
                ('zgodba', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.zgodba', verbose_name='Zgodba')),
            ],
            options={
                'verbose_name': 'Naloga',
                'verbose_name_plural': 'Naloge',
            },
        ),
        migrations.CreateModel(
            name='Komentar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('besedilo', ckeditor.fields.RichTextField(verbose_name='Vsebina komentarja')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('clan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.clan', verbose_name='Član')),
                ('zgodba', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.zgodba', verbose_name='Zgodba')),
            ],
            options={
                'verbose_name': 'Komentar',
                'verbose_name_plural': 'Komentarji',
            },
        ),
        migrations.CreateModel(
            name='Dokumentacija',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('naslov', models.CharField(blank=True, max_length=255, null=True, verbose_name='Naslov dokumentacije')),
                ('tip', models.IntegerField(choices=[(0, 'Uporabniška'), (1, 'Administratorska'), (2, 'Razvijalska')], verbose_name='Tip dokumentacije')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('projekt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.projekt', verbose_name='Projekt')),
            ],
            options={
                'verbose_name': 'Dokumentacija',
                'verbose_name_plural': 'Dokumentacije',
            },
        ),
        migrations.CreateModel(
            name='DailyScrum',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('have_done', ckeditor.fields.RichTextField(verbose_name='What have you done since the last meeting?')),
                ('will_do', ckeditor.fields.RichTextField(verbose_name='What are you planning to do until next meeting?')),
                ('problems', ckeditor.fields.RichTextField(verbose_name='Have you experienced any problems or issues?')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('projekt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.projekt', verbose_name='Projekt')),
            ],
            options={
                'verbose_name': 'DailyScrum',
                'verbose_name_plural': 'DailyScrumI',
            },
        ),
        migrations.AddField(
            model_name='clan',
            name='projekt',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.projekt', verbose_name='Projekt'),
        ),
        migrations.AddField(
            model_name='clan',
            name='uporabnik',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Uporabnik'),
        ),
        migrations.CreateModel(
            name='ScrumMaster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('projekt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.projekt', verbose_name='Projekt')),
                ('uporabnik', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Uporabnik')),
            ],
            options={
                'verbose_name': 'Scrum Master',
                'verbose_name_plural': 'Scrum Master',
                'unique_together': {('projekt', 'uporabnik')},
            },
        ),
        migrations.CreateModel(
            name='ProjectOwner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('projekt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.projekt', verbose_name='Projekt')),
                ('uporabnik', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Uporabnik')),
            ],
            options={
                'verbose_name': 'Project Owner',
                'verbose_name_plural': 'Project Owner',
                'unique_together': {('projekt', 'uporabnik')},
            },
        ),
        migrations.CreateModel(
            name='BelezenjeCasa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zacetek', models.DateTimeField(verbose_name='Čas začetka')),
                ('konec', models.DateTimeField(verbose_name='Čas konca')),
                ('presoja', models.CharField(max_length=255, verbose_name='Končna presoja')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('clan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.clan', verbose_name='Član')),
                ('naloga', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='website.naloga', verbose_name='Naloga')),
            ],
            options={
                'verbose_name': 'Beleženja časa',
                'verbose_name_plural': 'Zabeležen čas',
                'unique_together': {('clan', 'naloga')},
            },
        ),
    ]
