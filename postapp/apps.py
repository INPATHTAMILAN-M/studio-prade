from django.apps import AppConfig


class PostappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'postapp'

class Post_Link_Config(AppConfig):
    name = 'post_link'
 
    def ready(self):
        import post_link.signals