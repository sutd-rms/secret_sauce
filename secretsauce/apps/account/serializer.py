from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

# User Serializer
from secretsauce.apps.account.models import MyUser, MyUserManager


class MyUserSerializer(serializers.ModelSerializer):
  class Meta:
    model = MyUser
    fields = ('username', 'rmstoken', 'password', 'email')

  def create(self, validated_data):
    username = validated_data.pop('username')
    password = validated_data.pop('password')
    user = MyUser.objects.create_user(username=username, password=password, **validated_data)
    return user



class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ('id', 'username', 'email')

# Register Serializer
class RegisterSerializer(serializers.ModelSerializer):
  user = UserSerializer(required=True)

  class Meta:
    model = MyUser
    fields = "__all__"
    extra_kwargs = {'password': {'write_only': True}, 'rmstoken': {'write_only': True}}

  def create(self, validated_data):
    user_data = validated_data.pop('user')
    password = validated_data.pop('password')
    user = MyUser.objects.create_user(user_data, password, **validated_data)
    user.set_password(password)
    user.save()
    authuser = User.objects.create(user, **user_data)
    authuser.set_password(password)
    authuser.save()
    # user = User.objects.create_user(validated_data['username'], validated_data['email'], validated_data['password'], validated_data['rmstoken'])
    return user

# Login Serializer
class LoginSerializer(serializers.Serializer):
  username = serializers.CharField()
  password = serializers.CharField()

  def validate(self, data):
    user = authenticate(**data)
    # authuser = User.objects.create_user(username=data['username'])
    if user:
      return user
    raise serializers.ValidationError("Wrong Username or Password!")