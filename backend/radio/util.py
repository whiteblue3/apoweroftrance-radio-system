import random
from datetime import datetime, timedelta
from dateutil.tz import tzlocal
from django.db.models import Q


def now():
    return str(datetime.now(tz=tzlocal()).isoformat())


def get_random_track(channel, samples):
    from .models import (
        Track, PlayQueue
    )

    # According to International Radio Law, Once played track cannot restream in 3 hours
    now = datetime.now(tz=tzlocal())
    delta_3hour = timedelta(hours=3)
    base_time = now - delta_3hour

    filters = Q(channel__icontains=channel)

    # Except now playing
    queue_list = PlayQueue.objects.filter(channel__icontains=channel).order_by('id').distinct()
    if queue_list.count() > 0:
        nowplay = queue_list[0]
        filters = filters and Q(track_id__ne=nowplay.track.id)

    tracks = Track.objects.filter(
        (
            Q(last_played_at__lt=base_time) | Q(last_played_at=None)
        ) and filters
    )
    if tracks.count() < 1:
        # If service music is too little, ignore International Radio Law.
        tracks = Track.objects.filter(
            filters
        )

    count_track = tracks.count()
    if count_track > samples:
        count_track = samples
    random_tracks = random.sample(list(tracks), count_track)

    return random_tracks
