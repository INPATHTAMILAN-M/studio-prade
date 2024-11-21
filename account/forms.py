from django import forms
from django.contrib.auth.forms import AuthenticationForm

#Django inbuild Login Form
class CustomAuthForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        self.error_messages['invalid_login'] = 'Incorrect username or password'
        super(CustomAuthForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = "Enter Email"
        self.fields['password'].label = "Enter Password"