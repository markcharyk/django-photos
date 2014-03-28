from django import forms


class AlbumForm(forms.Form):
    OPTIONS = (
        (True, ("Public (Can be seen by any user)")),
        (False, ("Private (Only visible to you)"))
    )
    title = forms.CharField()
    privacy = forms.ChoiceField(choices=OPTIONS)


class PhotoForm(forms.Form):
    image = forms.FileField()
    caption = forms.CharField()


class TagForm(forms.Form):
    title = forms.CharField()
