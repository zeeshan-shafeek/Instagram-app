from django.contrib import admin
from .models import InstaUser, Conversation, Message, SocialPage

admin.site.register(SocialPage)
admin.site.register(InstaUser)
admin.site.register(Conversation)
admin.site.register(Message)

