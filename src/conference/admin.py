from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(VideoChatUser)
admin.site.register(VideoChatRoom)
admin.site.register(Signal)
admin.site.register(VideoChatMessages)
admin.site.register(VideoChatFile)
