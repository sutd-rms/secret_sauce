
# Create your models here.
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import User, AbstractUser
from django.db import models
from django.db.models import OneToOneField
from django.utils import timezone



class MyUserManager(BaseUserManager):
    def create_user(self, username, password, **extra_fields):
        # for i in request_data:
        # print("*" * 100, extra_fields)
        user = self.model(username= username, **extra_fields)
        user.set_password(password)
        user.save()
        return user


class MyUser(AbstractBaseUser):
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=64, default="pw")
    username = models.CharField(max_length=64)
    rmstoken = models.CharField(max_length=64)

    objects = MyUserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['username', 'email', 'rmstoken']
    # user_info = OneToOneField(to=User, on_delete=models.CASCADE, related_name="user")




# class RegisterForm(forms.ModelForm):
#     password
#     def save(self, *arg, **kwargs):
#         if not self.pk:
#             try:
#                 p = MyUser.objects.get(user=self.user)
#                 self.pk = p.pk
#             except MyUser.DoesNotExist:
#                 pass
#         super(MyUser, self).save(*arg, **kwargs)
