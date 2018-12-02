# Generated by Django 2.1.3 on 2018-12-02 05:04

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BankInformation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('guid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('account_number', models.CharField(max_length=15, unique=True)),
                ('is_active', models.BooleanField(default=False)),
                ('holder', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='customers.Customer')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BankStatement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('is_debit', models.BooleanField(default=False)),
                ('bank_info', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mutations', to='administrations.BankInformation')),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiver', to='customers.Customer')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender', to='customers.Customer')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]