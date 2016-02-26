from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    name = 'django_moj_template'
    verbose_name = 'MoJ Template'
