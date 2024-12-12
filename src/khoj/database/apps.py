# 导入Django的AppConfig类
from django.apps import AppConfig


# 定义一个名为DatabaseConfig的类，继承自AppConfig
class DatabaseConfig(AppConfig):
    # 设置默认的自动字段类型为BigAutoField
    default_auto_field = "django.db.models.BigAutoField"
    # 设置应用的名称为khoj.database
    name = "khoj.database"
