from django import forms
from .models import FORMAT, CHANNEL, Track


class UpdateTrackForm(forms.ModelForm):
    artist = forms.CharField(required=True)
    title = forms.CharField(required=True)
    description = forms.Textarea()
    channel = forms.MultipleChoiceField(choices=CHANNEL, required=True)

    class Meta:
        model = Track
        fields = ['artist', 'title', 'description', 'channel']

    # def save(self, commit=True):
    #     pass


class UploadTrackForm(UpdateTrackForm):
    audio = forms.FileField(required=True)
    format = forms.ChoiceField(choices=FORMAT, required=True)

    class Meta:
        model = Track
        fields = ['audio', 'format', 'artist', 'title', 'description', 'channel']

    # def save(self, commit=True):
    #     pass
