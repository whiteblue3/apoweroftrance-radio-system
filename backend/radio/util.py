import os
import random
import json
import redis
from datetime import datetime, timedelta
from dateutil.tz import tzlocal
from django.db.models import Q


def now():
    return str(datetime.now(tz=tzlocal()).isoformat())


def connect_redis():
    redis_host = os.environ.get('REDIS_URL')
    redis_port = os.environ.get('REDIS_PORT')
    return redis.StrictRedis(host=redis_host, port=redis_port, db=0)


def get_redis_data(channel):
    redis_server = connect_redis()

    raw_json = redis_server.get(channel)
    if raw_json is None:
        default_data = {
            "now_playing": None,
            "playlist": None
        }
        redis_server.set(channel, json.dumps(default_data, ensure_ascii=False).encode('utf-8'))
    try:
        data_json = json.loads(raw_json)
    except Exception as e:
        print('redis error: {}'.format(e))
        return None
    return dict(data_json)


def set_redis_data(channel, key, value):
    redis_server = connect_redis()

    redis_data = get_redis_data(channel)
    redis_data[key] = value
    redis_server.set(channel, json.dumps(redis_data, ensure_ascii=False).encode('utf-8'))


def get_random_track(channel, samples):
    from .models import (
        Track
    )

    # Remove last played track from queue
    now_play_track_id = None
    last_play_track_id = None
    try:
        redis_data = get_redis_data(channel)
        now_playing = redis_data["now_playing"]
        playlist = redis_data["playlist"]
    except IndexError:
        pass
    else:
        try:
            if now_playing:
                now_play_track_id = now_playing["id"]
        except KeyError:
            pass

        try:
            if playlist:
                last_play_track_id = playlist[-1]["id"]
        except KeyError:
            pass
        except IndexError:
            pass

    # According to International Radio Law, Once played track cannot restream in 3 hours
    now = datetime.now(tz=tzlocal())
    delta_3hour = timedelta(hours=3)
    base_time = now - delta_3hour

    filters = Q(channel__icontains=channel)

    # Except now playing
    if now_play_track_id is not None:
        filters = filters and ~Q(id=now_play_track_id)

    # Except last play
    if last_play_track_id is not None and now_play_track_id != last_play_track_id:
        filters = filters and ~Q(id=last_play_track_id)

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
