from base64 import b64encode
from os import urandom

from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.conf import settings
from django.views import View
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

import requests

from user.models import User
from account.models import Account

# ServiceM8
client_id = settings.CLIENT_ID
client_secret = settings.CLIENT_SECRET

authorize_url = 'https://go.servicem8.com/oauth/authorize'
access_token_url = 'https://go.servicem8.com/oauth/access_token'
redirect_uri = 'https://invisible-fence-ms.herokuapp.com/authenticate/callback/'

# Functions to retrieve info
def get_vendors(access_token):
    url = 'https://api.servicem8.com/api_1.0/vendor.json'
    headers = {'Authorization':'Bearer {}'.format(access_token)}
    vendors = requests.get(url, headers=headers).json()
    return vendors

def generate_password():
    random_bytes = urandom(12)
    token = b64encode(random_bytes).decode('utf-8')
    return token

class InitiateView(View):
    def get(self, request, *args, **kwargs):
        return redirect('https://go.servicem8.com/oauth/authorize?response_type=code&client_id={}&scope=read_jobs%20vendor%20read_customers%20read_job_categories&redirect_uri={}'.format(client_id, redirect_uri))

class CallbackView(View):
    def get(self, request, *args, **kwargs):
        code = self.request.GET.get('code', '')
        payload = {
            'grant_type':'authorization_code',
            'client_id':client_id,
            'client_secret':client_secret,
            'code':code,
            'redirect_uri':redirect_uri,
        }
        r = requests.post(access_token_url, data=payload).json()
        print(r)
        for vendor in get_vendors(r['access_token']):
            email = vendor['email']
            username = vendor['email'].split('@')[0]
            user, created = User.objects.get_or_create(
                email=vendor['email'],
                username=username,
            )
            if created:
                password = generate_password()
                user.set_password(password)
                user.save()
                print("User saved")
                account = Account(user=user, company=vendor['name'], website=vendor['website'], sm8_uuid=vendor['uuid'],
                                  access_token=r['access_token'], refresh_token=r['refresh_token'])
                account.save()
                # send_activation_email = requests.post(
                #     'https://api.mailgun.net/v3/mg.sm8attachments.com/messages',
                #     auth=('api', settings.MAILGUN_API),
                #     data={'from': 'Josh Sullivan <josh@misllc.com>',
                #           'to': [user.email],
                #           'subject': 'New Account for ServiceM8 Attachments',
                #           'text': 'Hi there,\n\nWe have created an account for you to access your attachments from ServiceM8. Each time you use our add-on from within ServiceM8, we add the zip file to your account at https://sm8attachments.com/attachment. You can access them anytime.\n\nYour credentials:\n\nUsername (email address): {}\n\nPassword: {}\n\nPlease let me know if you have any questions or issues. You can open a ticket here - http://bit.ly/mis_support.\n\nJosh Sullivan\n\nMagnolia Innovative Solutions'.format(user.email, password)}
                # )
                print("Email sent and account saved")
            else:
                update_account = Account.objects.get(user=user)
                update_account.access_token = r['access_token']
                update_account.refresh_token = r['refresh_token']
                update_account.save()
                print("Token updated")
        return redirect(
            '/authenticate/done/'
        )

class AuthDone(View):
    def get(self, request):
        return render(request, 'authenticate/done.html')