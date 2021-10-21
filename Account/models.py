from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class CustomDomain(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    domain_name = models.CharField(max_length=50,unique=True)

    def __str__(self):
        return self.domain_name
