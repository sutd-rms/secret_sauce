from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(verbose_name='email', max_length=255, unique=True)
    phone = models.CharField(null=True, max_length=255)
    token = models.CharField(max_length=60, null=False)
    REQUIRED_FIELDS = ['username', 'phone', 'first_name', 'last_name', 'token']
    USERNAME_FIELD = 'email'

    def get_username(self):
        return self.email