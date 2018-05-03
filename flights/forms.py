from django import forms
from django.forms import ModelForm, Form, ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction

class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'password1', 'password2')

    @transaction.atomic
    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.save()
        return user

    def is_valid(self):
        valid1 = super(RegistrationForm, self).is_valid()
        valid2 = True

        f_name = self.cleaned_data["first_name"]
        l_name = self.cleaned_data["last_name"]

        if not f_name.isalpha() or not f_name == f_name.title():
            self.add_error('first_name', 'Firstname has invalid format')
            valid2 = False

        if not l_name.isalpha() or not l_name == l_name.title():
            self.add_error('last_name', 'Lastname has invalid format')
            valid2 = False

        if not valid1 or not valid2:
            return False

        return True
