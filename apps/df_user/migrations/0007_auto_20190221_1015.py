# Generated by Django 2.0.10 on 2019-02-21 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('df_user', '0006_auto_20190220_1016'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='uemail',
            field=models.EmailField(default='', max_length=254, unique=True, verbose_name='邮箱'),
        ),
    ]
