from django.shortcuts import render,redirect

from url.models import ShortUrl

# Create your views here.

# Home page view
def Home(request):
    return render(request,'index.html')

# Short URL view
def url(request,name=None,query=None):
    # Check short URL validity
    if not name or name is None and not query or query is None:
        return render(request,'index.html')
    else:
        # IF short URL is exits and valid redirect to orginal url
        try:
            shorturl = 'url/'+name+'/'+query
            check = ShortUrl.objects.get(short_url=shorturl)
            check.visits = check.visits+1
            check.save()
            originalUrl = check.orginal_url
            return redirect(originalUrl)
        # Sent a error with short message
        except ShortUrl.DoesNotExist:
            return render(request,'index.html',{'error':'error'})