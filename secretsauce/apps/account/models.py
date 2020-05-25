from django.db import models
from django.contrib.auth.models import AbstractUser

# TODO: hash token field
class User(AbstractUser):
    email = models.EmailField(verbose_name='email', max_length=255, unique=True)
    phone = models.CharField(null=True, max_length=255)
    token = models.CharField(max_length=60, null=False)
    token_class = models.CharField(max_length=255)
    REQUIRED_FIELDS = ['username', 'phone', 'first_name', 'last_name', 'token', 'token_class']
    USERNAME_FIELD = 'email'

    def get_username(self):
        return self.email

    def get_token(self):
        return self.token

# TODO: hash token field
class Token(models.Model):
    token = models.CharField(max_length=60, unique=True)
    token_class = models.CharField(max_length=255)
