from django.shortcuts import render
from django.views import View
from django.http import HttpResponse

from .tasks import mail_labels

class GetLabelsView(View):
    def get(self, request):
        mail_labels.delay()
        return render(request, 'labels/labels_sent.html')