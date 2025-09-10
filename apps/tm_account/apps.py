from django.apps import AppConfig


class TmAccountConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tm_account"
    verbose_name = "사용자 계정 관리" # 관리자 페이지에 '사용자 계정 관리'라고 표시됨


    