# Generated by Django 3.2.18 on 2023-05-15 03:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Recording',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('demoTime', models.DateTimeField()),
                ('demoResult', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=50)),
                ('password', models.CharField(max_length=50)),
                ('pwdsuffix', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Track',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('aircraftType', models.IntegerField()),
                ('aircraftID', models.IntegerField(default=1)),
                ('coorX', models.DecimalField(decimal_places=3, max_digits=10)),
                ('coorY', models.DecimalField(decimal_places=3, max_digits=10)),
                ('speed', models.DecimalField(decimal_places=3, max_digits=10)),
                ('rank', models.IntegerField()),
                ('recordId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='frontEnd.recording')),
            ],
        ),
    ]
