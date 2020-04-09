from datetime import datetime
from dateutil.tz import tzlocal
from django_utils import storage


def now():
    return str(datetime.now(tz=tzlocal()).isoformat())


def upload_audio(request):
    # Upload file if file given
    try:
        filepath = storage.upload_file(request, 'audio', 'music', [
            "audio/mpeg", "audio/mp3",
            # "audio/aac", "audio/x-m4a", "audio/mp4", "audio/m4a"
        ])
        if filepath is not None:
            audio_path = filepath[0]

            # TODO: do something
    except Exception as e:
        raise e
