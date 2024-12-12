"""
Current format of khoj.yml
---
app:
    ...
content-type:
    ...
processor:
  conversation:
    offline-chat:
        enable-offline-chat: false
        chat-model: mistral-7b-instruct-v0.1.Q4_0.gguf
    ...
search-type:
    ...

New format of khoj.yml
---
app:
    ...
content-type:
    ...
processor:
  conversation:
    offline-chat:
        enable-offline-chat: false
        chat-model: NousResearch/Hermes-2-Pro-Mistral-7B-GGUF
    ...
search-type:
    ...
"""

import logging

from packaging import version

from khoj.utils.yaml import load_config_from_file, save_config_to_file

# 获取logger对象
logger = logging.getLogger(__name__)


# 迁移离线聊天默认模型
def migrate_offline_chat_default_model(args):
    # 定义schema版本
    schema_version = "1.7.0"
    raw_config = load_config_from_file(args.config_file)
    previous_version = raw_config.get("version")

    # 检查processor字段是否存在
    if "processor" not in raw_config:
        return args
    # 检查processor字段是否为空
    if raw_config["processor"] is None:
        return args
    # 检查conversation字段是否存在
    if "conversation" not in raw_config["processor"]:
        return args
    # 检查offline-chat字段是否存在
    if "offline-chat" not in raw_config["processor"]["conversation"]:
        return args
    # 检查chat-model字段是否存在
    if "chat-model" not in raw_config["processor"]["conversation"]["offline-chat"]:
        return args

    # 检查版本号是否小于schema版本号
    if previous_version is None or version.parse(previous_version) < version.parse(schema_version):
        logger.info(
            f"Upgrading config schema to {schema_version} from {previous_version} to change default (offline) chat model to mistral GGUF"
        )
        raw_config["version"] = schema_version

        # Update offline chat model to use Nous Research's Hermes-2-Pro GGUF in path format suitable for llama-cpp
        offline_chat_model = raw_config["processor"]["conversation"]["offline-chat"]["chat-model"]
        if offline_chat_model == "mistral-7b-instruct-v0.1.Q4_0.gguf":
            raw_config["processor"]["conversation"]["offline-chat"][
                "chat-model"
            ] = "NousResearch/Hermes-2-Pro-Mistral-7B-GGUF"

        save_config_to_file(raw_config, args.config_file)
    return args
