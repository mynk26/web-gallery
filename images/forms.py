from django.forms import Form, ModelForm
from django import forms
from.models import Images

class AddImageForm(Form):
    images = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

class SearchImageForm(Form):
    Image = forms.FileField()

class AddFolderForm(Form):
    Name = forms.CharField(max_length=50)

class AddFaceFolderForm(Form):
    Name = forms.CharField(max_length=50)
    Image = forms.FileField()
