# Generated by Django 4.0.1 on 2022-05-29 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('infra_custom', '0002_attribute_attributevalue_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='attribute',
            name='is_value_abbrev_required',
            field=models.BooleanField(default=False),
        ),
    ]
