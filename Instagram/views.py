from django.shortcuts import render, redirect
import requests

access_token = "this didnt work"
# Create your views here.
def home(request):

    id = 210007288341422
    redirect_uri = "https://127.0.0.1:8000%2Fapp%2Ftoken"
    client_id = 9023666841038430
    config_id = 172127899060667
    url = f'https://www.facebook.com/v16.0/dialog/oauth?client_id={client_id}&redirect_uri={redirect_uri}&state="%7Bst=state123abc,ds=123456789%7D"&config_id={config_id}'
    print(access_token)
    context = {
        'url': url
        }
    return render(request, 'dashboard.html', context)


def token(request):
    
    code = request.GET.get('code', '')
    context = {
        "code" : code
    }
    params = {
            'client_id': '139791198861160',
            'client_secret': 'bd6198dcc60a6a43ad94ebb7f6e9b4c8',
            'code': code,
            'redirect_uri': '<your_redirect_uri>'
        }
    response = requests.get('https://graph.facebook.com/v16.0/oauth/access_token', params=params)
    if response.status_code == 200:
        access_token = response.json()['access_token']
        # do something with the access_token
    else:
        # handle the error


