from django.urls import path

from . import views

app_name='labels'
urlpatterns = [
    path('email/', views.GetLabelsView.as_view(), name='get-labels'),
]