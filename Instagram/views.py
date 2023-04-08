from django.shortcuts import render, redirect
import requests
from .models import *
from django.contrib.auth.models import User
import json


app_id = 1178391262840909
app_secret = '8865398dc10f48900b9f3c57d83b93b8'
access_token = ''
redirect_uri = 'https://127.0.0.1:8000/app/token'
graph_uri = 'https://graph.facebook.com/v16.0/'


# Create your views here.
def home(request):

    
    permissions = 'email%2Cpages_show_list%2Cinstagram_basic%2Cinstagram_manage_comments%2Cinstagram_manage_insights%2Cinstagram_content_publish%2Cinstagram_manage_messages%2Cpages_read_engagement%2Cpages_manage_metadata%2Cpublic_profile'
    url = f'https://www.facebook.com/v16.0/dialog/oauth?client_id={app_id}&redirect_uri={redirect_uri}&scope={permissions}'
    # print(access_token)
    context = {
        'url': url
        }
    return render(request, 'dashboard.html', context)



def token(request):
    
    # when we reach on this page, we have gotten our first code and now we will send it to get our access token


    code = request.GET.get('code', '')
    context = {
        "code" : code
    }

    
    # print(code)
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
    
    data0 = response.json()

    # now that we have the access token, lets get the details of the user and make a new user

    user_response = requests.get(f'{graph_uri}me?fields=id,email,first_name,last_name&access_token={access_token}')
    data = user_response.json()

    username = user_response.json()['id']
    email = user_response.json()['email']
    first_name = user_response.json()['first_name']
    last_name = user_response.json()['last_name']

    if User.objects.filter(email=email).exists() or User.objects.filter(username=username).exists():
        
        user = User.objects.filter(username=username)
    else:
        user = User.objects.create_user(username=username, email=email, password="123qweasd")

    

    # by now we should have our user access code now we will send a get request to get page access token

    account_response = requests.get(f'{graph_uri}me/accounts?access_token={access_token}')
    accounts_data = account_response.json()['data']

    for page in accounts_data:
        access_token = page['access_token']
        page_id = page['id']
        fb_name = page['name']
        
        # check if SocialPage already exists with same fb_id  
        if not SocialPage.objects.filter(fb_id=page_id).exists():

            # create a new SocialPage object and save it to the database
            social_page = SocialPage(user=user, fb_name=fb_name, page_id=page_id, access_token=access_token)
            social_page.save()

    # now we have the data for all the pages for this specific user, now we can move on to saving all the conversation of every page

    for page in SocialPage.objects.filter(user=user):
        conversation_response = requests.get(f'{graph_uri}{page.page_id}/conversations?platform=instagram&access_token={page.access_token}')
        conversations_data = conversation_response.json()['data']
        for conversation in conversations_data:
            conversation_id = conversation['id']

            # check if conversation already exists with same id 
            if not Conversation.objects.filter(id=conversation_id).exists():

                # create a new conversation object and save it to the database
                conversation = Conversation(page=page, id= conversation_id)
                conversation.save()

    for page in SocialPage.objects.filter(user=user):
        for conversation in Conversation.objects.filter(id=page.page_id):
            messages_response = requests.get(f'{graph_uri}{conversation.id}?feilds=messages&access_token={page.access_token}')
            messages_response_dict = json.loads(messages_response)
            messages_data = messages_response_dict['messages']['data']
            for message in messages_data:
                message_id = message['id']

                # check if conversation already exists with same id 
                if not Message.objects.filter(id=message_id).exists():

                    # create a new conversation object and save it to the database
                    message = Message(conversation=conversation, id= message_id, )
                    conversation.save()



    

    context = {
        'status': status,
        'data0': data0,
        'data':data,
        
    }
    return render(request, 'token.html', context)

