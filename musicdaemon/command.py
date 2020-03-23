from serializable import Serializable

# Commands of CMD command properties
QUEUE = "queue"
UNQUEUE = "unqueue"


COMMAND_LIST = [QUEUE, UNQUEUE]


# Data of Queue command
class Queue(Serializable):
    # Track ID
    track_id = None

    # Queue track at date-time
    queue_at = None

    def __init__(self, track_id, queue_at=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.track_id = track_id
        self.queue_at = queue_at


# Data of UnQueue command
class UnQueue(Serializable):
    # Queue ID
    queue_id = None

    def __init__(self, queue_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue_id = queue_id


class CMD(Serializable):
    # Command queued host
    host = None

    target = None

    command = None

    # JSON formatted command data
    data = None

    def __init__(self, host, target, command, data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.host = host
        self.target = target
        self.command = command
        self.data = data
