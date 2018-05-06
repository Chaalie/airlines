from django import forms
from django.forms import ModelForm, Form, ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
import re

class RegistrationForm(Form):
    username = forms.CharField(
        label='Username',
        widget=forms.TextInput(attrs={'placeholder': ''}),
        max_length=32,
        help_text='Required. 30 characters or fewer. Alphanumeric characters only (letters, digits, hyphens and underscores).',
        required=True
    )
    first_name = forms.CharField(
        label='First Name',
        widget=forms.TextInput(attrs={'placeholder': ''}),
        max_length=32,
        help_text='Required. 30 characters or fewer. Latin letters and spaces only. Every word has to be capitalized.',
        required=True
    )
    last_name = forms.CharField(
        label='Last Name',
        widget=forms.TextInput(attrs={'placeholder': ''}),
        max_length=32,
        help_text='Required. 30 characters or fewer. Latin letters and spaces only. Every word has to be capitalized.',
        required=True
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': ''}),
        max_length=64,
        help_text='Required. At least 6 characters. Alphanumeric characters only (letters, digits, hyphens and underscores).',
        required=True
    )
    password2 = forms.CharField(
        label='Password confirmation',
        widget=forms.PasswordInput(attrs={'placeholder': ''}),
        max_length=64,
        help_text='Enter the same password as before, for verification.',
        required=True
    )

    def clean_username(self):
        username = self.cleaned_data['username']

        if not username:
            msg = 'You have to enter something.'
            self.add_error('username', msg)
            raise ValidationError('')

        if not re.match('^[A-Za-z0-9_-]+$', username):
            msg = 'Username can contain only alphanumeric characters.'
            self.add_error('username', msg)
            raise ValidationError('')

        return username

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']

        if not first_name:
            msg = 'You have to enter something.'
            self.add_error('first_name', msg)
            raise ValidationError('')

        if not all(c.isalpha() or c.isspace() for c in first_name):
            msg = 'First name can contain only latin characters and spaces.'
            self.add_error('first_name', msg)
            raise ValidationError('')

        if not first_name == first_name.title():
            msg = 'Every word has to be capitalized.'
            self.add_error('first_name', msg)
            raise ValidationError('')

        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']

        if not last_name:
            msg = 'You have to enter something.'
            self.add_error('last_name', msg)
            raise ValidationError('')

        if not all(c.isalpha() or c.isspace() for c in last_name):
            msg = 'First name can contain only latin characters and spaces.'
            self.add_error('last_name', msg)
            raise ValidationError('')

        if not last_name == last_name.title():
            msg = 'Every word has to be capitalized.'
            self.add_error('last_name', msg)
            raise ValidationError('')

        return last_name

    def clean_password2(self):
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']

        if not password1 and not password2:
            msg = 'You have to enter something.'
            self.add_error('password1', msg)
            self.add_error('password2', msg)
            raise ValidationError('')

        if not password1:
            msg = 'You have to enter something.'
            self.add_error('password1', msg)
            raise ValidationError('')

        if not password2:
            msg = 'You have to enter something.'
            self.add_error('password2', msg)
            raise ValidationError('')

        if not password1 == password2:
            msg = 'Passwords do not match.'
            self.add_error('password2', msg)
            raise ValidationError('')

        if not len(password1) >= 6:
            msg = 'Password has to contain at least 6 characters.'
            self.add_error('password1', msg)
            raise ValidationError('')

        if not re.match('^[A-Za-z0-9_-]+$', password1):
            msg = 'Password can contain only alphanumeric characters.'
            self.add_error('password1', msg)
            raise ValidationError('')

        return password2

    def is_valid(self):
        valid = super(RegistrationForm, self).is_valid()

        if not valid:
            return valid

        if User.objects.filter(username=self.cleaned_data['username']).exists():
            msg = 'This username is already taken.'
            self.add_error('username', msg)
            return False

        return True

    @transaction.atomic
    def save(self):
        user = User.objects.create_user(
            username   = self.cleaned_data['username'],
            first_name = self.cleaned_data['first_name'],
            last_name  = self.cleaned_data['last_name'],
            password   = self.cleaned_data['password1'],
            email      = None
        )
        user.save()
        return user
