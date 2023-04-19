from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class SocialPage(models.Model):
    user = models.OneToOneField(User, on_delete= models.CASCADE)
    fb_name =  models.CharField(max_length=200, null=False)
    page_id =models.CharField(max_length=20, null=False)
    access_token = models.CharField(max_length= 200)
    insta_username = models.CharField(max_length=200, null=False)

    def __str__(self):
        return self.fb_name + f" ({self.insta_username})"


class Conversation(models.Model):
    page = models.ForeignKey(SocialPage, on_delete= models.CASCADE)
    conversation_id = models.CharField(max_length=1000, null=False)

    def __str__(self):
        users = set([message.from_user for message in self.message_set.all()] + [message.to_user for message in self.message_set.all()])
        page_user = self.page.insta_username
        users = [user for user in users if user.username != page_user]
        username = ', '.join([str(user) for user in users])
        return f'Conversation with "{username}"'

class InstaUser(models.Model):
    user_id = models.CharField(max_length=200, null=False)
    username = models.CharField(max_length=200, null=False)

    def __str__(self):
        return self.username


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete= models.CASCADE)
    created_time = models.DateTimeField()
    message_id = models.CharField(max_length=1000, null=False)
    from_user = models.ForeignKey(InstaUser, on_delete=models.SET_DEFAULT, default=1, related_name='sent_messages')
    to_user = models.ForeignKey(InstaUser, on_delete=models.SET_DEFAULT, default=1, related_name='received_messages')
    message_body = models.CharField(max_length=1000, null=False)

    def __str__(self):
        return self.message_body


