# Generated by Django 2.2.16 on 2022-11-17 16:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_auto_20221117_2214'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='follow',
            name='name of constraint',
        ),
    ]