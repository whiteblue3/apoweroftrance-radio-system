import os
import sys
import io
import uuid
import json
import re
import argparse
import mimetypes
import requests
import progressbar
from os import listdir
from os.path import isfile, join
from mutagen.easyid3 import EasyID3


# auth_server = "auth.apoweroftrance.com"
# radio_server = "radio.apoweroftrance.com"

auth_server = "127.0.0.1:8081"
radio_server = "127.0.0.1:8080"


class MultiPartForm:
    """Accumulate the data to be used when posting a form."""

    def __init__(self):
        self.form_fields = []
        self.files = []
        # Use a large random byte string to separate
        # parts of the MIME data.
        self.boundary = uuid.uuid4().hex.encode('utf-8')
        return

    def get_content_type(self):
        return 'multipart/form-data; boundary={}'.format(
            self.boundary.decode('utf-8'))

    def add_field(self, name, value):
        """Add a simple field to the form data."""
        self.form_fields.append((name, value))

    def add_file(self, fieldname, filename, filedata,
                 mimetype=None):
        """Add a file to be uploaded."""
        body = filedata.read()
        if mimetype is None:
            mimetype = (
                mimetypes.guess_type(filename)[0] or
                'application/octet-stream'
            )
        self.files.append((fieldname, filename, mimetype, body))
        return

    @staticmethod
    def _form_data(name):
        return ('Content-Disposition: form-data; '
                'name="{}"\r\n').format(name).encode('utf-8')

    @staticmethod
    def _attached_file(name, filename):
        return ('Content-Disposition: file; '
                'name="{}"; filename="{}"\r\n').format(
                    name, filename).encode('utf-8')

    @staticmethod
    def _content_type(ct):
        return 'Content-Type: {}\r\n'.format(ct).encode('utf-8')

    def __bytes__(self):
        """Return a byte-string representing the form data,
        including attached files.
        """
        buffer = io.BytesIO()
        boundary = b'--' + self.boundary + b'\r\n'

        # Add the form fields
        for name, value in self.form_fields:
            buffer.write(boundary)
            buffer.write(self._form_data(name))
            buffer.write(b'\r\n')
            buffer.write(value.encode('utf-8'))
            buffer.write(b'\r\n')

        # Add the files to upload
        for f_name, filename, f_content_type, body in self.files:
            buffer.write(boundary)
            buffer.write(self._attached_file(f_name, filename))
            buffer.write(self._content_type(f_content_type))
            buffer.write(b'\r\n')
            buffer.write(body)
            buffer.write(b'\r\n')

        buffer.write(b'--' + self.boundary + b'--\r\n')
        return buffer.getvalue()


class UploadInChunks(object):
    def __init__(self, filepath, chunksize=1 << 13):
        self.filepath = filepath
        self.chunksize = chunksize
        self.totalsize = os.path.getsize(filepath)
        self.readsofar = 0
        self.bar = progressbar.ProgressBar(widgets=[progressbar.Percentage(), progressbar.Bar(), ' (', progressbar.Timer(), ' / ', progressbar.ETA(), ') '], maxval=100)

    def __iter__(self):
        with open(self.filepath, 'rb') as file:
            self.bar.start()
            while True:
                data = file.read(self.chunksize)
                if not data:
                    # sys.stderr.write("\n")
                    break
                self.readsofar += len(data)
                percent = self.readsofar * 1e2 / self.totalsize
                self.bar.update(percent)
                # sys.stderr.write("\r{percent:3.0f}%".format(percent=percent))
                yield data
            # sys.stderr.write("\n")
            self.bar.finish()
            # print("wait for finish upload...")

    def __len__(self):
        return self.totalsize


def authenticate(email, password):
    header = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    payload = {
        "email": email,
        "password": password
    }

    data = json.dumps(payload).encode('utf-8')

    host = auth_server
    api_request = "/v1/user/authenticate"

    r = requests.post("http://%s%s" % (host, api_request), headers=header, data=data, stream=True)
    data = r.json()

    if r.status_code == 200:
        return data["payload"]["token"]
    else:
        return None


def remove_tmp():
    base_dir = os.getcwd()
    os.system('rm -rf {0}/tmp'.format(base_dir))


def upload(token, directory, channel):
    host = radio_server
    api_request = "/v1/radio/upload"

    base_dir = os.getcwd()
    tmp_path = '{0}/tmp'.format(base_dir)
    if os.path.isdir(tmp_path):
        remove_tmp()
    os.mkdir('{0}/tmp'.format(base_dir))

    files = [f for f in listdir(directory) if isfile(join(directory, f))]

    print('Found files below:')
    for file in files:
        print('- {}'.format(file))
    sys.stderr.write("\n")
    print('-------------------------------------')
    sys.stderr.write("\n")
    for file in files:
        filepath = "{0}/{1}".format(directory, file)
        content_type, _ = mimetypes.guess_type(filepath)

        valid_mimetype = [
            "audio/mpeg", "audio/mp3"
        ]

        is_valid = False
        for mimetype in valid_mimetype:
            if mimetype == content_type:
                is_valid = True

        if is_valid is False:
            print("'{0}' is not support format".format(file))
            continue
        else:
            mp3info = EasyID3(filepath)
            artist = mp3info['artist'][0]
            title = mp3info['title'][0]

            form = MultiPartForm()
            form.add_file('audio', file, open(filepath, 'rb'), content_type)
            form.add_field('channel', channel)
            form.add_field('artist', artist)
            form.add_field('title', title)
            form.add_field('format', 'mp3')

            # extract meta information from title
            meta = re.match(r'\[\d\d\d\s.*\]', title).group()
            meta_split = meta.split(' ')
            if len(meta_split) > 0:
                bpm = meta_split[0][1:]
                if len(meta_split) > 1:
                    scale = meta_split[1].replace(']', '')
                else:
                    scale = None
                title = re.sub(r'\[\d\d\d\s.*\]\s', '', title)
                form.add_field('bpm', bpm)
                form.add_field('scale', scale)

            data = bytes(form)
            total_size = len(data)

            header = {
                "Authorization": "Bearer %s" % token,
                "Content-Type": form.get_content_type(),
                "Content-Length": str(total_size)
            }

            tmp = open('{0}/tmp/{1}'.format(base_dir, file), 'wb')
            tmp.seek(0)
            tmp.write(data)
            tmp.close()

            print("{0} - {1}:".format(artist, title))
            filename = '{0}/tmp/{1}'.format(base_dir, file)

            response = requests.post(
                "http://%s%s" % (host, api_request),
                headers=header,
                data=UploadInChunks(filename, chunksize=10),
                stream=True
            )

            if response.status_code == 201:
                print("OK")
            elif response.status_code == 403 or response.status_code == 401:
                print("Authentication Failed")
                exit()
            else:
                print("Failed")
            sys.stderr.write("\n")

    print('-------------------------------------')
    print("upload complete!!")
    remove_tmp()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A Power of Trance Music Uploader")
    parser.add_argument("--email", required=False, help="User Email")
    parser.add_argument("--password", required=False, help="User Password")
    parser.add_argument("--token", required=False, help="Auth JWT Token")
    parser.add_argument("--directory", required=False, help="Target Directory for Upload")
    parser.add_argument("--channel", required=False, help="Service Channel")

    args = parser.parse_args()

    sys.stderr.write("\n")
    print("####################################")
    print("#                                  #")
    print("# {} #".format(parser.description))
    print("#                                  #")
    print("####################################")
    print("version: 0.0.1")
    print("Auth Server: {}".format(auth_server))
    print("Radio Server: {}".format(radio_server))
    sys.stderr.write("\n")

    if args.token is None:
        if args.email is None:
            print("user 'email' is required")
            exit()

        if args.password is None:
            print("user 'password' is required")
            exit()
    else:
        if args.token is None:
            print("'token' is required when 'email', 'password' is not presented")
            exit()

    if args.directory is None:
        print("target 'directory' is required")
        exit()
    else:
        print("Upload Target Directory: {}".format(args.directory))

    if args.channel is None:
        print("service 'channel' is required")
        exit()
    else:
        print("Service Channel: {}".format(args.channel))

    sys.stderr.write("\n")

    token = None
    if args.token is None:
        token = authenticate(args.email, args.password)

        if token is None:
            print("Authentication Failed")
            exit()
        else:
            print("Authentication Successful!!")
    else:
        token = args.token
        print("Try use JWT Token")

    sys.stderr.write("\n")
    upload(token, args.directory, args.channel)
