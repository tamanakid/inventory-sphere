from django.apps import AppConfig


class InfraCustomConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'infra_custom'

    # def ready(self):
    #     import infra_custom.signals

