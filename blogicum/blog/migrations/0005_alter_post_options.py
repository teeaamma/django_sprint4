# Generated by Django 3.2.16 on 2024-11-10 14:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_post_comment_count'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-pub_date'], 'verbose_name': 'публикация', 'verbose_name_plural': 'Публикации'},
        ),
    ]