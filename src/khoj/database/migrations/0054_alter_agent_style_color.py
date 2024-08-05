# Generated by Django 5.0.7 on 2024-08-05 06:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("database", "0053_agent_style_color_agent_style_icon"),
    ]

    operations = [
        migrations.AlterField(
            model_name="agent",
            name="style_color",
            field=models.CharField(
                choices=[
                    ("blue", "Blue"),
                    ("green", "Green"),
                    ("red", "Red"),
                    ("yellow", "Yellow"),
                    ("orange", "Orange"),
                    ("purple", "Purple"),
                    ("pink", "Pink"),
                    ("teal", "Teal"),
                    ("cyan", "Cyan"),
                    ("lime", "Lime"),
                    ("indigo", "Indigo"),
                    ("fuchsia", "Fuchsia"),
                    ("rose", "Rose"),
                    ("sky", "Sky"),
                    ("amber", "Amber"),
                    ("emerald", "Emerald"),
                ],
                default="blue",
                max_length=200,
            ),
        ),
    ]