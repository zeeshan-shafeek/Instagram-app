from django.shortcuts import render, redirect
import requests
from .models import *
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import json
import requests
from datetime import datetime

app_id = 1178391262840909
app_secret = '8865398dc10f48900b9f3c57d83b93b8'
access_token = ''
redirect_uri = 'https://127.0.0.1:8000/app/token'
graph_uri = 'https://graph.facebook.com/v16.0/'


# Create your views here.
def home(request):
   
    permissions = ('email,'
                   'pages_show_list,'
                   'instagram_basic,'
                   'instagram_manage_comments,'
                   'instagram_manage_insights,'
                   'instagram_content_publish,'
                   'instagram_manage_messages,'
                   'pages_read_engagement,'
                   'pages_manage_metadata,'
                   'public_profile'
                   )
    
    url = f'https://www.facebook.com/v16.0/dialog/oauth?client_id={app_id}&redirect_uri={redirect_uri}&scope={permissions}'

    context = {
        'url': url
        }
    return render(request, 'dashboard.html', context)



def token(request):
    
    # when we reach on this page, we have gotten our first access code and now we will send it to get our access token


    code = request.GET.get('code', '')
    context = {
        "code" : code
    }

    

    params = {
            'client_id': app_id,
            'redirect_uri': redirect_uri,
            'client_secret': app_secret,
            'code': code,
            
        }
    response = requests.get(f'{graph_uri}oauth/access_token', params=params)
    
    if response.status_code == 200:
        access_token = response.json()['access_token']
        status = 'success'

    else:
        print(response.url)
        status = 'failure'
        data = ''

        context = {
        'status': status,
        'data':data,   
    }
        
        return render(request, 'token.html', context)
    
    
    # now that we have the access token, lets get the details of the user and make a new user

    user_fields = ('id,'
                   'email,'
                   'first_name,'
                   'last_name')
    
    user_response = requests.get(f'{graph_uri}me?fields={user_fields}&access_token={access_token}')
    
    
    
    # just for checking, will delete eventually
    data = user_response.json()

    username = user_response.json()['id']
    email = user_response.json()['email']
    first_name = user_response.json()['first_name']
    last_name = user_response.json()['last_name']

    if User.objects.filter(email=email).exists() or User.objects.filter(username=username).exists():
        
        user = User.objects.get(username=username)
    else:
        user = User.objects.create_user(username=username, email=email, first_name= first_name, last_name= last_name)

    

    # by now we should have our user access code now we will send a get request to get page access token

    account_response = requests.get(f'{graph_uri}me/accounts?access_token={access_token}')
    accounts_data = account_response.json()['data']

    for page in accounts_data:
        access_token = page['access_token']
        page_id = page['id']
        fb_name = page['name']
        

        insta_user_response = requests.get(f'{graph_uri}{page_id}?fields=instagram_accounts%7Busername%7D&access_token={access_token}')
        insta_username = insta_user_response.json()['instagram_accounts']['data'][0]['username']


        # check if SocialPage already exists with same fb_id  
        social_page, created = SocialPage.objects.update_or_create(
            page_id=page_id,
            defaults={
                'user': user,
                'fb_name': fb_name,
                'access_token': access_token,
                'insta_username': insta_username,
            }
        )
        

    # now we have the data for all the pages for this specific user, now we can move on to saving all the conversations for every page

    for page in SocialPage.objects.filter(user=user):
        message_fields = (
                        'created_time,'
                        'from,'
                        'id,'
                        'message,'
                        'to'
                        )
        
        conversation_fields = (f'id,messages%7B{message_fields}%7D')
        conversation_cursor = 'first'

        while conversation_cursor != '':

            if conversation_cursor == 'first':
                cursor_statement = ''
            else:
                cursor_statement = f'&after={conversation_cursor}'

            conversations_response = requests.get(
                f'{graph_uri}{page.page_id}/conversations?fields={conversation_fields}&platform=instagram&access_token={page.access_token}{cursor_statement}')
            
            conversations_data = conversations_response.json()['data']
            try:
                conversation_cursor = conversations_response.json()['paging']['cursors']['after']
                
            except KeyError:
                conversation_cursor = ''
            
            for conversation in conversations_data:

                conversation_id = conversation['id']

                # check if conversation already exists with same id 

                
                conversation_obj, created = Conversation.objects.update_or_create(
                    conversation_id= conversation_id,
                    defaults={
                        'page': page,
                    }
                )

                messages_data = conversation['messages']['data']
                
                # getting messages cursor for each conversation
                try:
                    messages_cursor = conversation['messages']['paging']['cursors']['after']
                except KeyError:
                    # we still need the while loop ahead to run atleast once so we can save all messages for the first time, so im saving the cursor like this
                    messages_cursor = 'no cursor found'

                # this loop that will keep running for the same conversation as long as we have a cursor
                while messages_cursor != '':
                    
                    for message in messages_data:

                        create_time= datetime.strptime(message['created_time'], '%Y-%m-%dT%H:%M:%S%z')                       

                        from_user, created = InstaUser.objects.update_or_create(
                            user_id= message['from']['id'],
                            defaults={
                                    'username': message['from']['username']
                            }
                        )

                        to_user, created = InstaUser.objects.update_or_create(
                            user_id= message['from']['id'],
                            defaults={

                                'username': message['to']['data'][0]['username']
                            }
                        )
                        
                        message_obj, created = Message.objects.update_or_create(
                            message_id = message['id'],
                            defaults={
                                'conversation':conversation_obj,
                                'created_time': create_time,
                                'from_user': from_user,
                                'to_user': to_user,
                                'message_body': message['message']
                            }
                        )
                    
                    # if there is no cursor found then we jump straight to the else part
                    if messages_cursor != 'no cursor found':

                        # the loop will never get to this part if the cursor was '', and here if there is a proper cursor, we can send an get request to get further messages and
                        # -save them in the same messages_data variable, which will go in the for loop aove and save messages.

                        messages_response = requests.get(f'{graph_uri}{conversation_id}/messages?fields={message_fields}&access_token={access_token}&after={messages_cursor}')

                        try:

                            # if this new response has a new cursor we can save that here so that it can be used the next time we get to this part.
                            
                            messages_cursor = messages_response.json()['paging']['cursors']['after']
                        except KeyError:

                            # we still need the loop to run for the new messages data we got, so setting it to this will make the loop run once again.
                            
                            messages_cursor = 'no cursor found'
                    
                        messages_data = messages_response.json()['data']
                        
                    else:
                        # here we set the cursor to '' so that the loop breaks
                        messages_cursor = ''
                    
    context = {
        'status': status,
        'data':data,
        
    }
    return render(request, 'token.html', context)

@csrf_exempt
def get_messages(request):
    return HttpResponse('pong')