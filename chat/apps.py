from django.apps import AppConfig

class ChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat'
    verbose_name = 'Чат'

    def ready(self):
        """Импортируем сигналы при загрузке приложения"""
        import chat.signals
