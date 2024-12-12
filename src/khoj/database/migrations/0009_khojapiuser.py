# 生成于 Django 4.2.5，于 2023-10-26 17:02

# 导入必要的模块和设置
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


# 定义迁移类
class Migration(migrations.Migration):
    # 定义依赖的迁移
    dependencies = [
        ("database", "0008_alter_conversation_conversation_log"),
    ]

    # 定义迁移操作
    operations = [
        # 创建 KhojApiUser 模型
        migrations.CreateModel(
            name="KhojApiUser",
            fields=[
                # 定义主键字段
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                # 定义唯一令牌字段
                ("token", models.CharField(max_length=50, unique=True)),
                # 定义名称字段
                ("name", models.CharField(max_length=50)),
                # 定义访问时间字段，允许为空
                ("accessed_at", models.DateTimeField(default=None, null=True)),
                # 定义用户外键字段，级联删除
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
