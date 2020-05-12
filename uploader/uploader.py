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
import asyncio
from os import listdir
from os.path import isfile, join
from mutagen.easyid3 import EasyID3


auth_server = "http://127.0.0.1:8081"
upload_server = "http://127.0.0.1:8082"


tasks = []


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
    def __init__(self, name, filepath, chunksize=1 << 13):
        self.filepath = filepath
        self.chunksize = chunksize
        self.totalsize = os.path.getsize(filepath)
        self.readsofar = 0
        self.name = name
        self.bar = progressbar.ProgressBar(widgets=[name, ': ', progressbar.Percentage(), progressbar.Bar(), ' (', progressbar.Timer(), ' / ', progressbar.ETA(), ') '], maxval=100)

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

    r = requests.post("%s%s" % (host, api_request), headers=header, data=data, stream=True)
    data = r.json()

    if r.status_code == 200:
        return data["payload"]["token"]
    else:
        return None


def remove_tmp():
    base_dir = os.getcwd()
    os.system('rm -rf {0}/tmp'.format(base_dir))


async def request_upload(host, api_request, header, filename, name):
    response = requests.post(
        "%s%s" % (host, api_request),
        headers=header,
        data=UploadInChunks(name, filename, chunksize=10)
    )
    if response.status_code == 201:
        print("OK")
    elif response.status_code == 403 or response.status_code == 401:
        print("Authentication Failed")
        exit()
    else:
        print("Failed")

    sys.stderr.write("\n")


def upload(token, file, channel):
    host = upload_server
    api_request = "/v1/upload/upload"

    base_dir = os.getcwd()
    tmp_path = '{0}/tmp'.format(base_dir)
    if os.path.isdir(tmp_path):
        remove_tmp()
    os.mkdir('{0}/tmp'.format(base_dir))

    # files = [f for f in listdir(directory) if isfile(join(directory, f))]

    # print('Upload File:')
    # # for file in files:
    # print('- {}'.format(file))
    # sys.stderr.write("\n")
    # print('-------------------------------------')
    # sys.stderr.write("\n")
    # for file in files:
    #     filepath = "{0}/{1}".format(directory, file)
    filepath = file
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
        return
    else:
        mp3info = EasyID3(filepath)
        artist = mp3info['artist'][0]
        title = mp3info['title'][0]

        if not artist or not title:
            print("Cannot upload because 'artist', 'title' tag is not exist")
            return

        form = MultiPartForm()
        form.add_file('audio', file, open(filepath, 'rb'), content_type)
        form.add_field('channel', channel)
        form.add_field('artist', artist)
        form.add_field('format', 'mp3')

        # extract meta information from title
        regex = re.match(r'\[\d\d\d\s.*\]', title)
        if regex:
            meta = regex.group()
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

        form.add_field('title', title)

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

        filename = '{0}/tmp/{1}'.format(base_dir, file)

        tasks.append(request_upload(host, api_request, header, filename, "{0} - {1}".format(artist, title)))

    # if len(tasks) > 0:
    if sys.version_info >= (3, 7):
        asyncio.run(asyncio.wait(tasks))
    else:
        loop = asyncio.get_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()

    print('-------------------------------------')
    print("upload complete!!")
    remove_tmp()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A Power of Trance Music Uploader")
    parser.add_argument("--email", required=True, help="User Email")
    parser.add_argument("--password", required=True, help="User Password")
    parser.add_argument("--file", required=True, help="Upload File")
    parser.add_argument("--channel", required=True, help="Service Channel")
    parser.add_argument("--authserver", required=False, help="Auth Server")
    parser.add_argument("--uploadserver", required=False, help="Upload Server")

    args = parser.parse_args()

    if args.authserver is not None:
        auth_server = args.authserver

    if args.uploadserver is not None:
        upload_server = args.uploadserver

    # sys.stderr.write("\n")
    # print("####################################")
    # print("#                                  #")
    # print("# {} #".format(parser.description))
    # print("#                                  #")
    # print("####################################")
    # print("version: 0.0.1")
    # print("Auth Server: {}".format(auth_server))
    # print("Upload Server: {}".format(upload_server))
    # sys.stderr.write("\n")

    if args.email is None:
        print("user 'email' is required")
        exit()

    if args.password is None:
        print("user 'password' is required")
        exit()

    if args.file is None:
        print("target 'file' is required")
        exit()
    # else:
    #     print("Upload File: {}".format(args.file))

    if args.channel is None:
        print("service 'channel' is required")
        exit()
    # else:
    #     print("Service Channel: {}".format(args.channel))

    sys.stderr.write("\n")

    token = authenticate(args.email, args.password)

    if token is None:
        print("Authentication Failed")
        exit()
    # else:
    #     print("Authentication Successful!!")

    # sys.stderr.write("\n")
    upload(token, args.file, args.channel)
