# THIS FILE IS TO STORE THE AUXILIARY FORMS WHERE WE ARE GOING TO RECEIVE THE USER DATA AND STORE IT
from django import forms


class CreateNewShortUrl(forms.Form):
    original_url = forms.CharField(label='original_url')