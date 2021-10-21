from django.urls import path
from . import views

app_name = 'Account'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='loginview'),
    path('registration/', views.RegistrationView.as_view(), name='Registration'),
    path('logout/', views.LogoutView.as_view(), name='Logoutview'),
    path('editaccount/', views.AccountView.as_view(), name='Accountview'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('password-reset/',views.PasswordRestView.as_view(), name='password-reset'),
    path('setnewpassword/<uidb64>/<token>/', views.SetnewPasswordView.as_view(), name='setnewpassword'),
]