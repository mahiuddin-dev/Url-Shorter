import re
from django.views.generic import View
from django.shortcuts import render,redirect, HttpResponseRedirect
from validate_email import validate_email
from django.contrib.auth import authenticate, login,logout,get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator,PasswordResetTokenGenerator
from django.utils.encoding import DjangoUnicodeDecodeError, force_bytes,force_text
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.contrib import messages
import threading
from .models import CustomDomain
from django.core.cache import cache

# Threading
class EmailThread(threading.Thread):
    def __init__(self,email_message):
        self.email_message = email_message
        threading.Thread.__init__(self)
    
    def run(self):
        self.email_message.send()

UserModel = get_user_model()

# Create your views here.
class RegistrationView(View):
    def get(self,request):
        # If user is already login
        if request.user.is_authenticated:
            return redirect('Home:Home')

        return render(request,'register.html')

    def post(self,request):
        # If user is already login
        if request.user.is_authenticated:
            return redirect('Home:Home')
        # User sing up data
        name = request.POST.get('name').title()
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirmPassword = request.POST.get('confirmPassword')

        context={
            'data':request.POST,
            'has_error': False
        }
        # Validation for email address
        if not validate_email(email):
            messages.error(request, 'Invalid email address')
            context['has_error'] = True
        # Password validation
        if password != confirmPassword:
            messages.error(request, "password don't match")
            context['has_error'] = True
        # Check database is email exists or not
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email address already exists')
            context['has_error'] = True
        # sent error message
        if context['has_error']:
            return render(request,'register.html',context)
        
        # Create user and save user in database
        user = User.objects.create_user(username = email, email = email)
        user.set_password(password)
        user.is_active = False
        user.first_name = name
        user.save()
        # Sent emmail to user verify email
        current_site = get_current_site(request)
        mail_subject = 'Verify your account'
        message = render_to_string('singUpToken.html', {
            'user': name,
            'site': current_site,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user)
        })
        sent_email = EmailMessage(mail_subject,message, to=[email])

        EmailThread(sent_email).start()

        messages.info(request, 'Account created successfully. For verify your account please check your email inbox or spam')

        return redirect('Account:loginview')

# Account activate function
def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = UserModel._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,User.DoesNotExist):
        user = None
    # Email verification  
    if user.is_active == False:
        if(user is not None and default_token_generator.check_token(user, token)):
            user.is_active = True
            user.save()
            messages.success(request, 'your account has been activated')
            
            current_site = get_current_site(request)
            mail_subject = 'Suessfully activated your account'
            message = render_to_string('Confirm.html', {
                'user': user.first_name,
                'site': current_site,
            })
            sent_email = EmailMessage(mail_subject,message, to=[user.email])
            EmailThread(sent_email).start()

            return redirect('Account:loginview')

        else:
            messages.warning(request, 'Activation link is invalid')
            return redirect('Account:Registration')
    else:
        messages.info(request, 'This account already activated')
        return redirect('Account:loginview')

# Account log in 
class LoginView(View):
    def get(self,request):
        # If user is already login
        if request.user.is_authenticated:
            return redirect('Home:Home')
        
        if request.method == 'GET':
            cache.set('next', request.GET.get('next', None))

        return render(request,'login.html')

    def post(self,request):
        # If user is already login
        if request.user.is_authenticated:
            return redirect('Home:Home')
        # User email and password taken from login page and verify user
        username = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request,username=username, password=password)
        # User verification successfully and redirect to home page
        if user is not None:
            login(request,user)
            next_url = cache.get('next')
            if next_url:
                cache.delete('next')
                return HttpResponseRedirect(next_url)

            return redirect('Home:Home')
        # User verification failed and redirect to login page with error message
        else:
            context = {'email': username}
            messages.error(request, 'Invalid email or password')
            return render(request,'login.html', context)

# Account Logout views
class LogoutView(LoginRequiredMixin,View):
    def get(self,request):
        logout(request)
        return redirect('Home:Home') # Logout successful and redirect to home page

# Password reset views
class PasswordRestView(View):
    def get(self,request):
        # If user is already login
        if request.user.is_authenticated:
            return redirect('Home:Home')

        return render(request,'reset.html')

    def post(self,request):
        # If user is already login
        if request.user.is_authenticated:
            return redirect('Home:Home')
        # take user email for password reset
        email = request.POST.get('email')
        # Check email validity if email is not valid redirect with error message
        if not validate_email(email):
            messages.error(request, 'Invalid email')
            return redirect('Account:password-reset')
        # Check email form database exists or not exists
        user = User.objects.filter(email=email)
        # If emial exists sent a token for reset password
        if user.exists():

            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            message = render_to_string('resetToken.html', {
                'site': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
                'token': PasswordResetTokenGenerator().make_token(user[0])
            })

            sent_email = EmailMessage(mail_subject,message, to=[email])

            EmailThread(sent_email).start()

            messages.success(request, 'You have sent you a email to reset your password. Check your email inbox or spam')
            return render(request,'reset.html')
        # if email is not exists redirect with error message
        else:
            messages.error(request, 'We can not find your email address')
            return redirect('Account:password-reset')

# password set view
class SetnewPasswordView(View):
    def get(self,request,uidb64,token):
        # If user is already login
        if request.user.is_authenticated:
            return redirect('Home:Home')

        context = {
            'uidb64': uidb64,
            'token': token
        }
        # Check password reset tokem
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            
            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.error(request, 'Password reset again. This is invalid link')
                return redirect('Authentication:password-reset')

        except DjangoUnicodeDecodeError as identifiere:
            messages.error(request, 'Someting went wrong')
            
        return render(request,'new-password.html',context)

    def post(self,request,uidb64,token):
        # If user is already login
        if request.user.is_authenticated:
            return redirect('Home:Home')

        context = {
            'uidb64': uidb64,
            'token': token,
            'has_error': False
        }
        # Collect new password from user
        password = request.POST.get('password')
        confirmPassword = request.POST.get('confirmPassword')

        # password validation
        if password != confirmPassword:
            messages.error(request, "password don't match")
            context['has_error'] = True

        if len(password) < 6:
            messages.error(request, "Pasword shoud be at least 6 characters long")
            context['has_error'] = True

        if context['has_error']:
            return render(request,'new-password.html',context)
        # Password changed successfully
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            mail_subject = 'Password changed successfully'
            message = "Your password has been changed successfully. if you think you don't changed, please contact our support"
            sent_email = EmailMessage(mail_subject,message, to=[user.email])
            EmailThread(sent_email).start()
            messages.success(request, 'Password reset successfully')
            return redirect('Account:loginview')
        # Sent a error message
        except DjangoUnicodeDecodeError as identifiere:
            messages.error(request, 'Someting went wrong')
            return render(request,'new-password.html')

# Account Edit
class AccountView(LoginRequiredMixin, View):
    # Remove space from string
    def removeSpace(self,string): 
        return string.replace(" ", "") 

    def get(self,request):
        # Context variables
        user = request.user
        cus_domain = CustomDomain.objects.filter(user=user)
        
        if len(cus_domain) > 0:
            context = {'cus_domain': cus_domain[0]}
        else:
            context = {'cus_domain': ''}

        return render(request,'account.html',context)
    
    def post(self,request):
        # Context variables
        user = request.user
        cus_domain = CustomDomain.objects.filter(user=user)
      
        if len(cus_domain) > 0:
            context = {'cus_domain': cus_domain[0]}
        else:
            context = {'cus_domain': ''}
   
        # Edit Account information
        if request.method=='POST' and 'updatedInfo' in request.POST:
            name = request.POST.get('fullname').title()
            email = request.POST.get('email')            
            # if name and email match
            if user.first_name == name and user.email == email:
                pass
            # if name or email don't match
            elif user.is_authenticated:
                # Emial don't match
                if user.email != email:
                    user.username = email
                    user.email = email
                    user.save()
                # IF name don't match
                if user.first_name != name:
                    user.first_name = name
                    user.save()
                # Sent emmail user to inform that account has been updated
                mail_subject = 'Account information changed'
                message = 'Account information updated successfully. if you think this is wrong, please contact our support'
                sent_email = EmailMessage(mail_subject,message, to=[user.email])
                EmailThread(sent_email).start()
                messages.success(request, 'Account information changed successfully')

        # CustomDomain 
        if request.method=='POST' and 'customDomain' in request.POST:
            # Collect custom name
            domainName = request.POST.get('domainName').lower()
            # Remove space from custom domain name
            domain = self.removeSpace(domainName)
            # Check domain exists
            allName = CustomDomain.objects.filter(domain_name=domain)
            
            # Custom name verification
            if len(domain) > 2:
                if len(allName) == 0:
                    if len(cus_domain) > 0:
                        cus_domain.update(domain_name=domain)
                        context = {'cus_domain': cus_domain[0]}
                        messages.success(request, 'Custom Domain edit successfully')
                        return redirect('Account:Accountview')
                    else:
                        custom_domain = CustomDomain(user=user, domain_name=domain)
                        custom_domain.save()
                        messages.success(request, 'Custom Domain created successfully')
                        return redirect('Account:Accountview')
                else:
                    messages.error(request, 'This name is already taken')
            else:
                messages.error(request, 'Name must be at least 2 characters long')

        return render(request,'account.html',context)