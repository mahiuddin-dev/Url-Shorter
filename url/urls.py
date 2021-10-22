from django.urls import path
from . import views

app_name = 'url'

urlpatterns = [
    path('', views.generaturlView.as_view(), name='generaturl'),
    path('shorturl/', views.ShortUrlList.as_view(), name='ShortUrl'),
]
