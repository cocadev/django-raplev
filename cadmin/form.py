from .models import Medias
from django import forms


class MediasForm(forms.ModelForm):
    class Meta:
        model = Medias
        fields = ('file', )
