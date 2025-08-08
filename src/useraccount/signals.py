from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver
from useraccount.models import Profile
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from django.conf import settings
from django.db.models.signals import m2m_changed
from django.dispatch import receiver




@receiver(user_logged_out)
def user_logged_out_handler(sender, request, **kwargs):
    if request.user.is_authenticated:
        Profile.objects.filter(id=request.user.id).update(online=False)
