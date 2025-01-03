# Generated by Django 4.2.4 on 2023-09-18 23:24

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("database", "0001_khojuser"),
    ]

    operations = [
        migrations.CreateModel(
            name="GoogleUser",
            fields=[
                # ID字段，自动创建，主键，不可序列化，verbose_name为"ID"
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                # sub字段，最大长度为200
                ("sub", models.CharField(max_length=200)),
                # azp字段，最大长度为200
                ("azp", models.CharField(max_length=200)),
                # email字段，最大长度为200
                ("email", models.CharField(max_length=200)),
                # name字段，最大长度为200
                ("name", models.CharField(max_length=200)),
                # given_name字段，最大长度为200
                ("given_name", models.CharField(max_length=200)),
                # family_name字段，最大长度为200
                ("family_name", models.CharField(max_length=200)),
                # picture字段，最大长度为200
                ("picture", models.CharField(max_length=200)),
                # locale字段，最大长度为200
                ("locale", models.CharField(max_length=200)),
                # user字段，一对一关系，关联到settings.AUTH_USER_MODEL，级联删除
                # 级联删除是指当关联的User对象被删除时，与之关联的Subscription对象也会被自动删除。
                (
                    "user",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
                ),
            ],
        ),
    ]
