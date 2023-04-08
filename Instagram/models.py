from django.db import models
from django.contrib.auth.models import User


class School(models.Model):
    name = models.CharField(max_length=50, null= False)
    Address = models.CharField(max_length=255, null= False)
    phone_no = models.CharField(max_length=255, null= False)
    details = models.CharField(max_length=1000, null= False)

    def __str__(self):
        return self.name



# Create your models here.


class SocialPage(models.Model):
    user = models.OneToOneField(User, on_delete= models.CASCADE)
    fb_name =  models.CharField(max_length=200, null=False)
    page_id =models.CharField(max_length=20, null=False)
    access_token = models.CharField(max_length= 200)


class Conversation(models.Model):
    page = models.ForeignKey(SocialPage, on_delete= models.CASCADE)
    id = models.CharField(max_length=1000, null=False)


class InstaUser(models.Model):
    id = models.CharField(max_length=200, null=False)
    username = models.CharField(max_length=200, null=False)


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete= models.CASCADE)
    created_time = models.DateTimeField()
    id = models.CharField(max_length=1000, null=False)
    from_user = models.ForeignKey(InstaUser, on_delete= models.CASCADE)
    to_user = models.ForeignKey(InstaUser, on_delete= models.CASCADE)
    message_body = models.CharField(max_length=1000, null=False)


