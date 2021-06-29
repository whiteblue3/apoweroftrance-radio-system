from datetime import timedelta
from django import forms
from django.conf import settings
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
from .util import now, get_is_pending_remove


class UpdateTrackForm(forms.ModelForm):
    audio = forms.FileField(required=False)
    format = forms.ChoiceField(choices=FORMAT, required=True)
    img = forms.FileField(required=False)

    artist = forms.CharField(required=True, max_length=70)
    title = forms.CharField(required=True, max_length=200)
    description = forms.Textarea()
    bpm = forms.IntegerField(required=False)
    scale = forms.CharField(required=False, max_length=15)
    queue_in = forms.TimeField(required=False)
    queue_out = forms.TimeField(required=False)
    mix_in = forms.TimeField(required=False)
    mix_out = forms.TimeField(required=False)
    ment_in = forms.TimeField(required=False)
    channel = forms.MultipleChoiceField(choices=CHANNEL, required=True)

    is_service = forms.BooleanField(required=False)
    is_ban = forms.BooleanField(required=False)
    ban_reason = forms.Textarea()

    class Meta:
        model = Track
        fields = ['audio', 'format', 'img', 'artist', 'title', 'description', 'bpm', 'scale',
                  'queue_in', 'queue_out', 'mix_in', 'mix_out', 'ment_in', 'channel', 'is_service', 'is_ban', 'ban_reason']

    def save(self, commit=True):
        f = self.cleaned_data['audio']
        audio_format = self.cleaned_data['format']
        img = self.cleaned_data['img']

        if audio_format not in SUPPORT_FORMAT:
            raise ValidationError(_("Unsupported music file format"))

        if get_is_pending_remove(self.instance.id):
            raise ValidationError(_("You cannot change information because the track reserved pending remove"))

        artist = self.cleaned_data['artist']
        title = self.cleaned_data['title']

        try:
            description = self.cleaned_data['description']
        except MultiValueDictKeyError:
            description = ""

        try:
            bpm = self.cleaned_data['bpm']
        except MultiValueDictKeyError:
            bpm = None

        try:
            scale = self.cleaned_data['scale']
        except MultiValueDictKeyError:
            scale = None

        try:
            queue_in = self.cleaned_data['queue_in']
        except MultiValueDictKeyError:
            queue_in = None

        try:
            queue_out = self.cleaned_data['queue_out']
        except MultiValueDictKeyError:
            queue_out = None

        try:
            mix_in = self.cleaned_data['mix_in']
        except MultiValueDictKeyError:
            mix_in = None

        try:
            mix_out = self.cleaned_data['mix_out']
        except MultiValueDictKeyError:
            mix_out = None

        try:
            ment_in = self.cleaned_data['ment_in']
        except MultiValueDictKeyError:
            ment_in = None

        channel = self.cleaned_data['channel']

        for service_channel in channel:
            if service_channel not in SERVICE_CHANNEL:
                raise ValidationError(_("Invalid service channel"))

        try:
            is_service = self.cleaned_data['is_service']
        except MultiValueDictKeyError:
            is_service = True

        try:
            is_ban = self.cleaned_data['is_ban']
        except MultiValueDictKeyError:
            is_ban = False

        try:
            ban_reason = self.cleaned_data['ban_reason']
        except MultiValueDictKeyError:
            ban_reason = ""

        duration = self.instance.duration
        filepath = self.instance.location

        if f is not None:
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

            duration = str(timedelta(seconds=float(duration)))

        cover_art_path = self.instance.cover_art

        if img is not None:
            try:
                storage_driver = settings.STORAGE_DRIVER
                valid_mimetype = [
                    "image/png"
                ]
                if valid_mimetype is not None:
                    cover_art_path = storage.upload_file_direct(img, 'cover_art', storage_driver, valid_mimetype)
                else:
                    raise ValidationError(_("Unsupported image file format"))
            except Exception as e:
                raise e

        self.instance.location = filepath
        self.instance.format = audio_format
        self.instance.cover_art = cover_art_path
        self.instance.artist = artist
        self.instance.title = title
        self.instance.description = description
        self.instance.bpm = bpm
        self.instance.scale = scale
        self.instance.queue_in = queue_in
        self.instance.queue_out = queue_out
        self.instance.mix_in = mix_in
        self.instance.mix_out = mix_out
        self.instance.ment_in = ment_in
        self.instance.duration = duration
        self.instance.channel = channel
        self.instance.is_service = is_service
        self.instance.is_ban = is_ban
        self.instance.ban_reason = ban_reason

        return super().save(commit=commit)


class UploadTrackForm(UpdateTrackForm):
    audio = forms.FileField(required=True)
    format = forms.ChoiceField(choices=FORMAT, required=True)
    img = forms.FileField(required=False)

    class Meta:
        model = Track
        exclude = ['user']
        fields = ['audio', 'format', 'img', 'artist', 'title', 'description', 'bpm', 'scale',
                  'queue_in', 'queue_out', 'mix_in', 'mix_out', 'ment_in', 'channel', 'is_service', 'is_ban', 'ban_reason']

    def save(self, commit=True):

        f = self.cleaned_data['audio']
        audio_format = self.cleaned_data['format']
        img = self.cleaned_data['img']

        if audio_format not in SUPPORT_FORMAT:
            raise ValidationError(_("Unsupported music file format"))

        artist = self.cleaned_data['artist']
        title = self.cleaned_data['title']

        try:
            description = self.cleaned_data['description']
        except MultiValueDictKeyError:
            description = ""

        try:
            bpm = self.cleaned_data['bpm']
        except MultiValueDictKeyError:
            bpm = None

        try:
            scale = self.cleaned_data['scale']
        except MultiValueDictKeyError:
            scale = None

        try:
            queue_in = self.cleaned_data['queue_in']
        except MultiValueDictKeyError:
            queue_in = None

        try:
            queue_out = self.cleaned_data['queue_out']
        except MultiValueDictKeyError:
            queue_out = None

        try:
            mix_in = self.cleaned_data['mix_in']
        except MultiValueDictKeyError:
            mix_in = None

        try:
            mix_out = self.cleaned_data['mix_out']
        except MultiValueDictKeyError:
            mix_out = None

        try:
            ment_in = self.cleaned_data['ment_in']
        except MultiValueDictKeyError:
            ment_in = None

        channel = self.cleaned_data['channel']

        for service_channel in channel:
            if service_channel not in SERVICE_CHANNEL:
                raise ValidationError(_("Invalid service channel"))

        try:
            is_service = self.cleaned_data['is_service']
        except MultiValueDictKeyError:
            is_service = True

        try:
            is_ban = self.cleaned_data['is_ban']
        except MultiValueDictKeyError:
            is_ban = False

        try:
            ban_reason = self.cleaned_data['ban_reason']
        except MultiValueDictKeyError:
            ban_reason = ""

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

        cover_art_path = None

        if img is not None:
            try:
                storage_driver = settings.STORAGE_DRIVER
                valid_mimetype = [
                    "image/png"
                ]
                if valid_mimetype is not None:
                    cover_art_path = storage.upload_file_direct(img, 'cover_art', storage_driver, valid_mimetype)
                else:
                    raise ValidationError(_("Unsupported image file format"))
            except Exception as e:
                raise e

        self.instance.user = self.user
        self.instance.location = filepath
        self.instance.format = audio_format
        self.instance.is_service = True
        self.instance.cover_art = cover_art_path
        self.instance.artist = artist
        self.instance.title = title
        self.instance.description = description
        self.instance.bpm = bpm
        self.instance.scale = scale
        self.instance.queue_in = queue_in
        self.instance.queue_out = queue_out
        self.instance.mix_in = mix_in
        self.instance.mix_out = mix_out
        self.instance.ment_in = ment_in
        self.instance.duration = str(timedelta(seconds=float(duration)))
        self.instance.play_count = 0
        self.instance.channel = channel
        self.instance.uploaded_at = now()
        self.instance.last_played_at = None
        self.instance.is_ban = is_ban
        self.instance.ban_reason = ban_reason

        return super().save(commit=commit)
