import random
from datetime import datetime, timedelta
from dateutil.tz import tzlocal
from django.db.models import Q


def now():
    return str(datetime.now(tz=tzlocal()).isoformat())


def get_random_track(channel, samples, is_delete_now_play=False):
    from .models import (
        Track, PlayQueue
    )

    # Remove last played track from queue
    now_play_track_id = None
    try:
        queue = PlayQueue.objects.filter(channel__icontains=channel).order_by('id').distinct()[0]
    except IndexError:
        pass
    else:
        now_play_track_id = queue.track.id
        if is_delete_now_play:
            queue.delete()

    # According to International Radio Law, Once played track cannot restream in 3 hours
    now = datetime.now(tz=tzlocal())
    delta_3hour = timedelta(hours=3)
    base_time = now - delta_3hour

    filters = Q(channel__icontains=channel)

    # Except now playing
    if now_play_track_id is not None:
        filters = Q(channel__icontains=channel) and ~Q(id=now_play_track_id)

    tracks = Track.objects.filter(
        (Q(last_played_at__lt=base_time) | Q(last_played_at=None)) and filters)

    if tracks.count() < 1:
        # If service music is too few, ignore International Radio Law.
        tracks = Track.objects.filter(filters)

    count_track = tracks.count()
    if count_track > samples:
        count_track = samples
    random_tracks = random.sample(list(tracks), count_track)

    return random_tracks
