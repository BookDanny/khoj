import csv
import json
from datetime import datetime, timedelta

from apscheduler.job import Job
from django.contrib import admin, messages
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.http import HttpResponse
from django_apscheduler.admin import DjangoJobAdmin, DjangoJobExecutionAdmin
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJob, DjangoJobExecution
from unfold import admin as unfold_admin

# 从khoj.database.models模块中导入以下类
from khoj.database.models import (
    # 代理类
    Agent,
    # AI模型API类
    AiModelApi,
    # 聊天模型选项类
    ChatModelOptions,
    # 客户端应用程序类
    ClientApplication,
    # 会话类
    # 条目类
    Conversation,
    # 导入Entry类
    Entry,
    # 导入GithubConfig类
    GithubConfig,
    # 导入KhojUser类
    KhojUser,
    # Notion配置
    NotionConfig,
    # 进程锁
    ProcessLock,
    # 反射性问题
    ReflectiveQuestion,
    # 搜索模型配置
    SearchModelConfig,
    # 服务器聊天设置
    ServerChatSettings,
    # 语音到文本模型选项
    SpeechToTextModelOptions,
    # 订阅
    Subscription,
    # 文本到图像模型配置
    TextToImageModelConfig,
    # 用户对话配置
    UserConversationConfig,
    # 用户请求
    UserRequests,
    # 用户语音模型配置
    UserVoiceModelConfig,
    # 声音模型选项
    VoiceModelOption,
    # 网络爬虫
    WebScraper,
)
from khoj.utils.helpers import ImageIntentType


class KhojDjangoJobAdmin(DjangoJobAdmin, unfold_admin.ModelAdmin):
    # 定义显示在列表中的字段
    list_display = (
        "id",
        "next_run_time",
        "job_info",
    )
    # 定义搜索字段
    search_fields = ("id", "next_run_time")
    # 定义排序字段
    ordering = ("-next_run_time",)
    # 创建一个DjangoJobStore对象
    job_store = DjangoJobStore()

    def job_info(self, obj):
        job: Job = self.job_store.lookup_job(obj.id)
        return f"{job.func_ref} {job.args} {job.kwargs}" if job else "None"

    job_info.short_description = "Job Info"  # type: ignore

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            jobs = [job.id for job in self.job_store.get_all_jobs() if search_term in str(job)]
            queryset |= self.model.objects.filter(id__in=jobs)
        return queryset, use_distinct


class KhojDjangoJobExecutionAdmin(DjangoJobExecutionAdmin, unfold_admin.ModelAdmin):
    pass


admin.site.unregister(DjangoJob)
admin.site.register(DjangoJob, KhojDjangoJobAdmin)
admin.site.unregister(DjangoJobExecution)
admin.site.register(DjangoJobExecution, KhojDjangoJobExecutionAdmin)


class GroupAdmin(BaseGroupAdmin, unfold_admin.ModelAdmin):
    pass


class UserAdmin(BaseUserAdmin, unfold_admin.ModelAdmin):
    pass


class KhojUserAdmin(UserAdmin, unfold_admin.ModelAdmin):
    # 定义一个过滤器，用于筛选出在指定日期之后加入的用户
    class DateJoinedAfterFilter(admin.SimpleListFilter):
        title = "Joined after"
        parameter_name = "joined_after"

        # 返回可供选择的日期范围
        def lookups(self, request, model_admin):
            return (
                ("1d", "Last 24 hours"),
                ("7d", "Last 7 days"),
                ("30d", "Last 30 days"),
                ("90d", "Last 90 days"),
            )

        # 根据选择的日期范围，返回筛选后的用户列表
        def queryset(self, request, queryset):
            if self.value():
                days = int(self.value().rstrip("d"))
                date_threshold = datetime.now() - timedelta(days=days)
                return queryset.filter(date_joined__gte=date_threshold)
            return queryset

    class HasGoogleAuthFilter(admin.SimpleListFilter):
        title = "Has Google Auth"
        parameter_name = "has_google_auth"

        def lookups(self, request, model_admin):
            return (("True", "True"), ("False", "False"))

        def queryset(self, request, queryset):
            if self.value() == "True":
                return queryset.filter(googleuser__isnull=False)
            if self.value() == "False":
                return queryset.filter(googleuser__isnull=True)

    list_display = (
        "id",
        "email",
        "username",
        "phone_number",
        "is_active",
        "uuid",
        "is_staff",
        "is_superuser",
    )
    search_fields = ("email", "username", "phone_number", "uuid")
    filter_horizontal = ("groups", "user_permissions")

    list_filter = (
        HasGoogleAuthFilter,
        DateJoinedAfterFilter,
        "verified_email",
    ) + UserAdmin.list_filter

    fieldsets = (
        (
            "Personal info",
            {"fields": ("phone_number", "email_verification_code", "verified_phone_number", "verified_email")},
        ),
    ) + UserAdmin.fieldsets

    actions = ["get_email_login_url"]

    def get_email_login_url(self, request, queryset):
        for user in queryset:
            if user.email:
                host = request.get_host()
                unique_id = user.email_verification_code
                login_url = f"{host}/auth/magic?code={unique_id}"
                messages.info(request, f"Email login URL for {user.email}: {login_url}")

    get_email_login_url.short_description = "Get email login URL"  # type: ignore


# 注销Group模型
admin.site.unregister(Group)
# 注册KhojUser模型，并使用KhojUserAdmin类
admin.site.register(KhojUser, KhojUserAdmin)

# 注册ProcessLock模型，并使用unfold_admin.ModelAdmin类
admin.site.register(ProcessLock, unfold_admin.ModelAdmin)
# 注册SpeechToTextModelOptions模型，并使用unfold_admin.ModelAdmin类
admin.site.register(SpeechToTextModelOptions, unfold_admin.ModelAdmin)
# 注册ReflectiveQuestion模型到admin站点，使用unfold_admin.ModelAdmin作为管理类
admin.site.register(ReflectiveQuestion, unfold_admin.ModelAdmin)
# 注册ClientApplication模型到admin站点，使用unfold_admin.ModelAdmin作为管理类
admin.site.register(ClientApplication, unfold_admin.ModelAdmin)
# 注册GithubConfig模型到admin站点，使用unfold_admin.ModelAdmin作为管理类
admin.site.register(GithubConfig, unfold_admin.ModelAdmin)
# 注册NotionConfig模型到admin站点，使用unfold_admin.ModelAdmin作为管理类
admin.site.register(NotionConfig, unfold_admin.ModelAdmin)
# 注册UserVoiceModelConfig模型到admin站点，使用unfold_admin.ModelAdmin作为管理类
admin.site.register(UserVoiceModelConfig, unfold_admin.ModelAdmin)
# 注册VoiceModelOption模型到admin站点，使用unfold_admin.ModelAdmin作为管理类
admin.site.register(VoiceModelOption, unfold_admin.ModelAdmin)
# 注册UserRequests模型到admin站点，使用unfold_admin.ModelAdmin作为管理类
admin.site.register(UserRequests, unfold_admin.ModelAdmin)


@admin.register(Agent)
class AgentAdmin(unfold_admin.ModelAdmin):
    list_display = (
        "id",
        "name",
    )
    search_fields = ("id", "name")
    list_filter = ("privacy_level",)
    ordering = ("-created_at",)


@admin.register(Entry)
class EntryAdmin(unfold_admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
        "updated_at",
        "user",
        "agent",
        "file_source",
        "file_type",
        "file_name",
        "file_path",
    )
    search_fields = ("id", "user__email", "user__username", "file_path")
    list_filter = (
        "file_type",
        "user__email",
        "search_model__name",
    )
    ordering = ("-created_at",)


@admin.register(Subscription)
class KhojUserSubscription(unfold_admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "type",
    )

    search_fields = ("id", "user__email", "user__username", "type")
    list_filter = ("type",)


@admin.register(ChatModelOptions)
class ChatModelOptionsAdmin(unfold_admin.ModelAdmin):
    list_display = (
        "id",
        "chat_model",
        "ai_model_api",
        "max_prompt_size",
    )
    search_fields = ("id", "chat_model", "ai_model_api__name")


@admin.register(TextToImageModelConfig)
class TextToImageModelOptionsAdmin(unfold_admin.ModelAdmin):
    list_display = (
        "id",
        "model_name",
        "model_type",
    )
    search_fields = ("id", "model_name", "model_type")


@admin.register(AiModelApi)
class AiModelApiAdmin(unfold_admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "api_key",
        "api_base_url",
    )
    search_fields = ("id", "name", "api_key", "api_base_url")


@admin.register(SearchModelConfig)
class SearchModelConfigAdmin(unfold_admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "bi_encoder",
        "cross_encoder",
    )
    search_fields = ("id", "name", "bi_encoder", "cross_encoder")


@admin.register(ServerChatSettings)
class ServerChatSettingsAdmin(unfold_admin.ModelAdmin):
    list_display = (
        "chat_default",
        "chat_advanced",
        "web_scraper",
    )


@admin.register(WebScraper)
class WebScraperAdmin(unfold_admin.ModelAdmin):
    list_display = (
        "priority",
        "name",
        "type",
        "api_key",
        "api_url",
        "created_at",
    )
    search_fields = ("name", "api_key", "api_url", "type")
    ordering = ("priority",)


# 使用admin模块注册Conversation模型
@admin.register(Conversation)
class ConversationAdmin(unfold_admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "created_at",
        "updated_at",
        "client",
    )
    search_fields = ("id", "user__email", "user__username", "client__name")
    list_filter = ("agent", "client", "user")
    ordering = ("-created_at",)

    actions = ["export_selected_objects", "export_selected_minimal_objects"]

    def export_selected_objects(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="conversations.csv"'

        writer = csv.writer(response)
        writer.writerow(["id", "user", "created_at", "updated_at", "conversation_log"])

        for conversation in queryset:
            modified_log = conversation.conversation_log
            chat_log = modified_log.get("chat", [])
            for idx, log in enumerate(chat_log):
                if log["by"] == "khoj" and log["images"]:
                    log["images"] = ["inline image redacted for space"]
                    chat_log[idx] = log

            modified_log["chat"] = chat_log

            writer.writerow(
                [
                    conversation.id,
                    conversation.user,
                    conversation.created_at,
                    conversation.updated_at,
                    json.dumps(modified_log),
                ]
            )

        return response

    export_selected_objects.short_description = "Export selected conversations"  # type: ignore

    def export_selected_minimal_objects(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="conversations.csv"'

        writer = csv.writer(response)
        writer.writerow(["id", "user", "created_at", "updated_at", "conversation_log"])

        fields_to_keep = set(["message", "by", "created"])

        for conversation in queryset:
            return_log = dict()
            chat_log = conversation.conversation_log.get("chat", [])
            for idx, log in enumerate(chat_log):
                updated_log = {key: log[key] for key in fields_to_keep}
                # 如果日志中的by字段为khoj，并且intent字段存在，并且intent字段中的type字段存在，并且type字段的值在TEXT_TO_IMAGE或TEXT_TO_IMAGE_V3中
                if (
                    log["by"] == "khoj"
                    and log["intent"]
                    and log["intent"]["type"]
                    and log["intent"]["type"]
                    in [
                        ImageIntentType.TEXT_TO_IMAGE.value,
                        ImageIntentType.TEXT_TO_IMAGE_V3.value,
                    ]
                ):
                    updated_log["message"] = "inline image redacted for space"
                chat_log[idx] = updated_log
            return_log["chat"] = chat_log

            writer.writerow(
                [
                    conversation.id,
                    conversation.user,
                    conversation.created_at,
                    conversation.updated_at,
                    json.dumps(return_log),
                ]
            )

        return response

    export_selected_minimal_objects.short_description = "Export selected conversations (minimal)"  # type: ignore

    # 获取用户请求的动作
    def get_actions(self, request):
        # 调用父类的get_actions方法，获取动作列表
        actions = super().get_actions(request)
        # 如果用户不是超级用户
        if not request.user.is_superuser:
            if "export_selected_objects" in actions:
                del actions["export_selected_objects"]
            if "export_selected_minimal_objects" in actions:
                del actions["export_selected_minimal_objects"]
        return actions


@admin.register(UserConversationConfig)
class UserConversationConfigAdmin(unfold_admin.ModelAdmin):
    # 定义UserConversationConfigAdmin类，继承自unfold_admin.ModelAdmin
    list_display = (
        "id",
        "get_user_email",
        "get_chat_model",
        "get_subscription_type",
    )
    # 定义列表显示的字段
    search_fields = ("id", "user__email", "setting__chat_model", "user__subscription__type")
    # 定义搜索字段
    ordering = ("-updated_at",)

    def get_user_email(self, obj):
        return obj.user.email

    get_user_email.short_description = "User Email"  # type: ignore
    get_user_email.admin_order_field = "user__email"  # type: ignore

    def get_chat_model(self, obj):
        return obj.setting.chat_model if obj.setting else None

    get_chat_model.short_description = "Chat Model"  # type: ignore
    get_chat_model.admin_order_field = "setting__chat_model"  # type: ignore

    def get_subscription_type(self, obj):
        if hasattr(obj.user, "subscription"):
            return obj.user.subscription.type
        return None

    get_subscription_type.short_description = "Subscription Type"  # type: ignore
    get_subscription_type.admin_order_field = "user__subscription__type"  # type: ignore
