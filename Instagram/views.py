from django.shortcuts import render, redirect
import requests
from .models import *
from django.contrib.auth.models import User


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
        data = ''

        context = {
        'status': status,
        'data':data,
        
    }
        return render(request, 'token.html', context)
    
    
    # now that we have the access token, lets get the details of the user and make a new user

    user_response = requests.get(f'{graph_uri}me?fields=id,email,first_name,last_name&access_token={access_token}')
    
    
    
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
        
        # check if SocialPage already exists with same fb_id  
        if not SocialPage.objects.filter(page_id=page_id).exists():

            # create a new SocialPage object and save it to the database
            social_page = SocialPage(user=user, fb_name=fb_name, page_id=page_id, access_token=access_token)
            social_page.save()
        else:
            social_page = SocialPage.objects.get(page_id=page_id)

    # now we have the data for all the pages for this specific user, now we can move on to saving all the conversations for every page

    for page in SocialPage.objects.filter(user=user):
        conversation_fields = ('id,'
                               'messages'
                                    '{created_time,'
                                    'from,'
                                    'id,'
                                    'message,'
                                    'to}'
                               )

        conversations_response = requests.get(f'{graph_uri}{page.page_id}/conversations?fields={conversation_fields}&platform=instagram&access_token={page.access_token}')
        conversations_data = conversations_response.json()['data']
        for conversation in conversations_data:

            conversation_id = conversation['id']

            # check if conversation already exists with same id 
            if not Conversation.objects.filter(conversation_id= conversation_id).exists():

                conversation_obj = Conversation(page=page, conversation_id= conversation_id)
                conversation_obj.save()
            else:
                conversation_obj = Conversation.objects.get(conversation_id= conversation_id)


            messages_data = conversation['messages']['data']
            for message in messages_data:

                message_id = message['id']

                # check if message already exists with same id 
                if not Message.objects.filter(message_id=message_id).exists():

                    create_time= datetime.strptime(message['created_time'], '%Y-%m-%dT%H:%M:%S%z')
                    if not InstaUser.objects.filter(user_id= message['from']['id']):
                        from_user = InstaUser(user_id= message['from']['id'], username= message['from']['username'])
                        from_user.save()
                    else:
                        from_user = InstaUser.objects.get(user_id= message['from']['id'])

                    if not InstaUser.objects.filter(user_id= message['to']['data'][0]['id']):
                        to_user = InstaUser(user_id= message['to']['data'][0]['id'], username= message['to']['data'][0]['username'])
                        to_user.save()
                    else:
                        to_user = InstaUser.objects.get(user_id= message['to']['data'][0]['id'])

                    message_obj = Message(conversation= conversation_obj,
                                            created_time= create_time,
                                            message_id= message['id'],
                                            from_user=from_user,
                                            to_user=to_user,
                                            message_body=message['message'])
                    message_obj.save()


    context = {
        'status': status,
        'data':data,
        
    }
    return render(request, 'token.html', context)







    """conversation_response = requests.get(f'{graph_uri}{page.page_id}/conversations?platform=instagram&access_token={page.access_token}')
        conversations_data = conversation_response.json()['data']
        for conversation in conversations_data:
            conversation_id = conversation['id']

            # check if conversation already exists with same id 
            if not Conversation.objects.filter(id=conversation_id).exists():

                # create a new conversation object and save it to the database
                conversation = Conversation(page=page, id= conversation_id)
                conversation.save()


    # now that we have all conversations, we can get every message 
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
                    message = Message(conversation=conversation, id= message_id, message_body="message loading...")
                    message.save()



    

    context = {
        'status': status,
        'data0': data0,
        'data':data,
        
    }
    return render(request, 'token.html', context)

"""