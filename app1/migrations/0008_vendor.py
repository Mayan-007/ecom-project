# Generated by Django 3.2.19 on 2023-06-05 03:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1', '0007_order'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('password', models.CharField(max_length=100)),
                ('address', models.TextField()),
                ('phone', models.CharField(max_length=100)),
            ],
        ),
    ]