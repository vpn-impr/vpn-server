# Generated by Django 5.1.2 on 2024-10-15 05:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servers', '0004_outlineserver_host_outlineserver_port_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='outlineserverkey',
            name='port',
            field=models.CharField(default='None', max_length=10000),
        ),
    ]