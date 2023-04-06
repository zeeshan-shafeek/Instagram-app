from django.shortcuts import render, redirect

access_token = "this didnt work"
# Create your views here.
def home(request):

    id = 210007288341422
    permissions = "pages_show_list%2Cinstagram_basic%2Cinstagram_manage_comments%2Cinstagram_manage_insights%2Cinstagram_content_publish%2Cinstagram_manage_messages%2Cpages_read_engagement%2Cpages_manage_metadata%2Cpublic_profile"
    redirect_uri = "https://127.0.0.1:8000%2Fapp%2Ftoken"
    url = f"https://www.facebook.com/v16.0/dialog/oauth?response_type=code&display=page&client_id={id}&redirect_uri={redirect_uri}&auth_type=rerequest&scope={permissions}"

    print(access_token)
    context = {
        'url': url
        }
    return render(request, 'dashboard.html', context)


def token(request):
    access_token = request.GET.get('access_token', '')
    context = {
        "access_token" : access_token
    }
    return render(request, 'token.html', context)


