# Generated by Django 4.1.5 on 2023-01-19 01:46

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CrossTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Meaning',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=200, validators=[django.core.validators.MinLengthValidator(1, 'Title must be greater than 1 characters')])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('text', 'owner')},
            },
        ),
        migrations.CreateModel(
            name='Word',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('writing', models.CharField(max_length=200, validators=[django.core.validators.MinLengthValidator(1, 'Title must be greater than 1 characters')])),
                ('old_writing', models.CharField(max_length=200)),
                ('transcription', models.CharField(max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('meanings', models.ManyToManyField(through='cards.CrossTable', to='cards.meaning')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('writing', 'owner')},
            },
        ),
        migrations.AddField(
            model_name='crosstable',
            name='meaning',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cards.meaning'),
        ),
        migrations.AddField(
            model_name='crosstable',
            name='word',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cards.word'),
        ),
    ]
