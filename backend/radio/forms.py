from datetime import timedelta
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ValidationError
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.easyid3 import EasyID3
from django_utils import storage
from .models import (
    FORMAT, CHANNEL, SUPPORT_FORMAT, FORMAT_MP3, FORMAT_M4A,
    SERVICE_CHANNEL, Track
)
from .util import now


class UpdateTrackForm(forms.ModelForm):
    artist = forms.CharField(required=True)
    title = forms.CharField(required=True)
    description = forms.Textarea()
    channel = forms.MultipleChoiceField(choices=CHANNEL, required=True)

    class Meta:
        model = Track
        fields = ['artist', 'title', 'description', 'channel']

    def save(self, commit=True):
        artist = self.cleaned_data['artist']
        title = self.cleaned_data['title']

        try:
            description = self.cleaned_data['description']
        except MultiValueDictKeyError:
            description = ""

        channel = self.cleaned_data['channel']

        for service_channel in channel:
            if service_channel not in SERVICE_CHANNEL:
                raise ValidationError(_("Invalid service channel"))

        self.instance.artist = artist
        self.instance.title = title
        self.instance.description = description
        self.instance.channel = channel

        return super().save(commit=commit)


class UploadTrackForm(UpdateTrackForm):
    audio = forms.FileField(required=True)
    format = forms.ChoiceField(choices=FORMAT, required=True)

    class Meta:
        model = Track
        fields = ['audio', 'format', 'artist', 'title', 'description', 'channel']

    def save(self, commit=True):
        f = self.cleaned_data['audio']
        audio_format = self.cleaned_data['format']

        if audio_format not in SUPPORT_FORMAT:
            raise ValidationError(_("Unsupported music file format"))

        artist = self.cleaned_data['artist']
        title = self.cleaned_data['title']

        try:
            description = self.cleaned_data['description']
        except MultiValueDictKeyError:
            description = ""

        channel = self.cleaned_data['channel']

        for service_channel in channel:
            if service_channel not in SERVICE_CHANNEL:
                raise ValidationError(_("Invalid service channel"))

        duration = None
        filepath = None

        try:
            storage_driver = settings.STORAGE_DRIVER
            valid_mimetype = None
            if audio_format == FORMAT_MP3:
                valid_mimetype = [
                    "audio/mpeg", "audio/mp3"
                ]
            elif audio_format == FORMAT_M4A:
                valid_mimetype = [
                    "audio/aac", "audio/x-m4a", "audio/mp4", "audio/m4a"
                ]
            if valid_mimetype is not None:
                filepath = storage.upload_file_direct(f, 'music', storage_driver, valid_mimetype)
            else:
                raise ValidationError(_("Unsupported music file format"))
        except Exception as e:
            raise e

        if audio_format == FORMAT_MP3:
            audio = MP3(f, ID3=EasyID3)
            duration = audio.info.length

        elif audio_format == FORMAT_M4A:
            audio = MP4(f)
            duration = audio.info.length

        User = get_user_model()
        user = User.objects.get(id=self.user.id)

        self.instance = Track(
            user=user,
            location=filepath,
            format=audio_format,
            is_service=True,
            artist=artist,
            title=title,
            description=description,
            duration=str(timedelta(seconds=float(duration))),
            play_count=0,
            channel=channel,
            uploaded_at=now(),
            last_played_at=None
        )

        return super().save(commit=commit)
