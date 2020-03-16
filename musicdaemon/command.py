from serializable import Serializable


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
