from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class ShortUrl(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    orginal_url = models.URLField(max_length=200)
    short_url = models.CharField(max_length=200, unique=True)
    visits = models.IntegerField(default=0)

    def __str__(self):
        return self.orginal_url[0:20]+' => '+ self.short_url[0:20]
    
