from django.urls import path

from . import views

app_name = 'authenitcate'
urlpatterns = [
    path('', views.InitiateView.as_view(), name='sm8-initiate'),
    path('callback/', views.CallbackView.as_view(), name='sm8-callback'),
    path('done/', views.AuthDone.as_view(), name='auth-done'),
]