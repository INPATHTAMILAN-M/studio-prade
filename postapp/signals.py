from django.db.models.signals import post_save, pre_delete
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Post_Link
 
 

  
@receiver(post_save, sender=Post_Link)
def save_profile(sender, instance, **kwargs):
        instance.post_link.save()