from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import *



class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name',
                  'email', 'password1', 'password2']

class editUser(ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]


class editGuest(ModelForm):
    class Meta:
        model = Guest
        fields = ["phoneNumber"]

