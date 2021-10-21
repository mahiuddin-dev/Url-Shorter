from django.shortcuts import render,redirect
from django.utils.crypto import get_random_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.contrib import messages
from django.http import JsonResponse
import json

from .models import ShortUrl
from Account.models import CustomDomain

# Create your views here.

# Short url generat view
class generaturlView(LoginRequiredMixin,View):
    # Create rendom string for short url
    def randomString(self):
        unique_id = get_random_string(length=6)
        return unique_id
    # Check custom domain exists or not
    def CheckCustomDomain(self,request,srt_url):
        user = request.user
        custom_domain = CustomDomain.objects.filter(user=user)
        # If don't have Custom Domain. short link exp (short/inputchar)
        if not custom_domain: 
            name = 'short'
            short_url = 'url/'+name+'/'+srt_url
            return short_url
        # If have Custom Domain. short link exp (customname/inputchar)
        else:
            custom_name = str(custom_domain[0])
            short_url = 'url/'+custom_name+'/'+srt_url
            return short_url


    def get(self,request):
        # Context variables
        user = request.user
        current_site = get_current_site(request)
        scheme = request.scheme
        short_url = ShortUrl.objects.filter(user=user).order_by('-id')[:4]

        context = {
            'short_url':short_url,
            'scheme':scheme,
            'current_site':current_site,
          }
        return render(request,'generator.html', context)

    def post(self,request):
        current_site = get_current_site(request)
        scheme = request.scheme
     
        user = request.user 
        # Context variable  
        short_url_list = ShortUrl.objects.filter(user=user).order_by('-id')[:4]
        
        if request.method == 'POST':

            # Generat user based input
            if request.POST['original'] and request.POST['short_url']:
                
                original = request.POST['original']
                srt_url = request.POST['short_url']
                
                short_url = self.CheckCustomDomain(request,srt_url)
                
                # Check short url exist or not
                check_short_url = ShortUrl.objects.filter(short_url=short_url)
               
                # If short url not exists
                if not check_short_url:
                    newurl = ShortUrl(user=user,orginal_url=original, short_url=short_url)
                    newurl.save()
                    context = {
                        'short_url':short_url_list,
                        'scheme':scheme,
                        'current_site':current_site,
                    }
                    return render(request,'generator.html',context)
                # If short url exists
                else:
                    messages.error(request, 'Short url already exists. Try another')
                    context = {
                        'short_url':short_url_list,
                        'orginal': original,
                        'scheme':scheme,
                        'current_site':current_site,
                    }
                    return render(request,'generator.html',context)

            # Generat short url randomly
            elif request.POST['original']:
                original = request.POST['original']
                isGenerated = False

                while not isGenerated:
                    srt_url = self.randomString()
                    short_url = self.CheckCustomDomain(request,srt_url)
                    # Check short url exist or not
                    check_short_url = ShortUrl.objects.filter(short_url=short_url)

                    # If short url not exists
                    if not check_short_url:
                        newurl = ShortUrl(user=user,orginal_url=original, short_url=short_url)
                        newurl.save()
                        context = {
                            'short_url':short_url_list,
                            'scheme':scheme,
                            'current_site':current_site,
                        }
                        return render(request,'generator.html',context)
                    # If short url exists
                    else:
                        continue
            else:
                messages.error(request, 'Please fill all fields')

        return render(request,'generator.html', {'short_url':short_url_list})

# Shoe all short urls
class ShortUrlList(LoginRequiredMixin,View):

    def ShortUrl(self,request):
        current_site = get_current_site(request)
        scheme = request.scheme
        user = request.user
        shorturl= ShortUrl.objects.filter(user=user).order_by('-id')
        context= {'allshorturl':shorturl,'current_site':current_site,'scheme':scheme}
        return render(request,'urlList.html',context)

    def get(self, request):
        return self.ShortUrl(request)
    
    def post(self, request):
        return self.ShortUrl(request)


# Delete short url view   
def UpdateLink(request):
    data = json.loads(request.body)
    shortlinkId = data['shortlinkId']
    print(shortlinkId)
    action = data['action']

    user = request.user
    shorturl = ShortUrl.objects.get(user=user,pk=shortlinkId)
    # Delete short url
    if action == 'remove':
        shorturl.delete()

    return JsonResponse('Item was added', safe=False)


