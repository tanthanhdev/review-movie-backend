# Generated by Django 3.2.7 on 2021-12-20 21:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_alter_video_published_at'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cast',
            options={'ordering': ('pk',)},
        ),
        migrations.AlterField(
            model_name='product',
            name='status',
            field=models.CharField(blank=True, choices=[('In Production', 'In Production'), ('Released', 'Released')], max_length=100, null=True),
        ),
    ]
