# 生成此迁移文件时使用的Django版本为4.2.5，时间为2023年10月13日02:39

# 导入必要的模块
import uuid

# 从Django的迁移框架和模型框架中导入必要的类
from django.db import migrations, models


# 定义一个迁移类，用于描述数据库模式的变更
class Migration(migrations.Migration):
    # 定义此迁移依赖的其他迁移
    dependencies = [
        # 此迁移依赖"database"应用中的名为"0004_content_types_and_more"的迁移
        ("database", "0004_content_types_and_more"),
    ]

    # 定义此迁移要执行的操作
    operations = [
        # 在"embeddings"模型中添加一个新字段"corpus_id"
        migrations.AddField(
            model_name="embeddings",
            name="corpus_id",
            # 设置字段为UUID类型，使用uuid.uuid4作为默认值，且不可编辑
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
    ]
