from __future__ import absolute_import, unicode_literals
from celery import shared_task

import os

from django.http import JsonResponse
from django.core.mail import EmailMessage
from django.conf import settings

import csv
import requests
import datetime

from account.models import Account

def get_company(company_uuid, access_token):
    url = 'https://api.servicem8.com/api_1.0/company/{}.json'.format(company_uuid)
    headers = {'Authorization': 'Bearer {}'.format(access_token)}
    r = requests.get(url, headers=headers)
    company = r.json()
    return company

def get_category(access_token):
    url = 'https://api.servicem8.com/api_1.0/category.json'
    headers = {'Authorization': 'Bearer '.format(access_token)}
    categories = requests.get(url, headers=headers).json()
    for category in categories:
        print(category)
        if category['name'] == 'Battery Replacement':
            print(category['name'])
            return category['uuid']

@shared_task
def mail_labels():
    account = Account.objects.get(pk=2)
    today = datetime.date.today()
    file_name = 'labels_{}.csv'.format(today)
    new_tokens = requests.post('https://go.servicem8.com/oauth/access_token',
                               data={
                                   'grant_type': 'refresh_token',
                                   'client_id': settings.CLIENT_ID,
                                   'client_secret': settings.CLIENT_SECRET,
                                   'refresh_token': account.refresh_token,
                               }).json()
    account.access_token = new_tokens['access_token']
    account.refresh_token = new_tokens['refresh_token']
    account.save()
    print("Tokens updated")
    jobs_url = "https://api.servicem8.com/api_1.0/job.json?%24filter=category_uuid%20eq%20'022eb836-d5a9-4704-8541-fffc32e14ebb'"
    headers = {'Authorization': 'Bearer {}'.format(account.access_token)}
    jobs = requests.get(jobs_url, headers=headers).json()
    with open('files/{}'.format(file_name), 'w+') as csv_file:
        fieldnames = ['name', 'street', 'city', 'state', 'zip_code', 'job_description']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for job in jobs:
            date = job['date']
            datetime_object = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            if today.year == datetime_object.year and today.month == datetime_object.month:
                print("Month, year, and category match")
                company_info = get_company(job['company_uuid'], account.access_token)
                print(company_info)
                name = company_info['name']
                street = company_info['address_street']
                city = company_info['address_city']
                state = company_info['address_state']
                zip_code = company_info['address_postcode']
                job_description = job['job_description']
                print("Creating labels")
                writer.writerow(
                    {
                        'name': name,
                        'street': street,
                        'city': city,
                        'state': state,
                        'zip_code': zip_code,
                        'job_description': job_description
                    }
                )
    email = EmailMessage(
        'Monthly Label List',
        'Hi there, please find your monthly label list attached to this email.\n\nThank you.\n\nJosh Sullivan\nMagnolia Innovative Solutions',
        'josh@misllc.com',
        [account.user.email],
    )
    email.attach_file('files/{}'.format(file_name))
    email.send()
    print("Email sent")
    os.remove('files/{}'.format(file_name))
    print("File removed")
    return file_name
