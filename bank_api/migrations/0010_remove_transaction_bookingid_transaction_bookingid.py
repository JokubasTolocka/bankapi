# Generated by Django 4.2.1 on 2023-05-12 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank_api', '0009_alter_transaction_bookingid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='bookingId',
        ),
        migrations.AddField(
            model_name='transaction',
            name='bookingID',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
    ]
