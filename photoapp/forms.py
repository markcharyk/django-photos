from django import forms


class AlbumForm(forms.Form):
    title = forms.CharField()


class PhotoForm(forms.Form):
    image = forms.FileField()
    caption = forms.CharField()


class TagForm(forms.Form):
    title = forms.CharField()
