import io
import google.auth
from google.auth import compute_engine, app_engine
from google.cloud import storage
from google.auth.transport.requests import AuthorizedSession
from google.resumable_media import requests, common
from django.conf import settings


project_id = settings.GCP_PROJECT_ID
bucket_name = settings.GCP_STORAGE_BUCKET_NAME

try:
    # Try local development environment
    credentials, project_id = google.auth.default()
except:
    # Try production environment
    try:
        credentials = compute_engine.Credentials()
    except:
        credentials = app_engine.Credentials()

client = storage.Client(credentials=credentials, project=project_id)
bucket = client.get_bucket(bucket_name)


class GCSObjectStreamUpload(object):
    """
    Example)
    client = storage.Client()

    with GCSObjectStreamUpload(client=client, bucket_name='test-bucket', blob_name='test-blob') as s:
        for _ in range(1024):
            s.write(b'x' * 1024)
    """
    def __init__(
        self,
        client: storage.Client,
        bucket_name: str,
        blob_name: str,
        mimetype: str='application/octet-stream',
        chunk_size: int=256 * 1024
    ):
        self._client = client
        self._bucket = self._client.bucket(bucket_name)
        self._blob = self._bucket.blob(blob_name)
        self._mimetype = mimetype

        self._buffer = b''
        self._buffer_size = 0
        self._chunk_size = chunk_size
        self._read = 0

        self._transport = AuthorizedSession(
            credentials=self._client._credentials
        )
        self._request = None  # type: requests.ResumableUpload

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, *_):
        if exc_type is None:
            self.stop()

    def start(self):
        url = (
            f'https://www.googleapis.com/upload/storage/v1/b/'
            f'{self._bucket.name}/o?uploadType=resumable'
        )
        self._request = requests.ResumableUpload(
            upload_url=url, chunk_size=self._chunk_size
        )
        self._request.initiate(
            transport=self._transport,
            content_type=self._mimetype,
            stream=self,
            stream_final=False,
            metadata={'name': self._blob.name},
        )

    def stop(self):
        self._request.transmit_next_chunk(self._transport)

    def write(self, data: bytes) -> int:
        data_len = len(data)
        self._buffer_size += data_len
        self._buffer += data
        del data
        while self._buffer_size >= self._chunk_size:
            try:
                self._request.transmit_next_chunk(self._transport)
            except common.InvalidResponse:
                self._request.recover(self._transport)
        return data_len

    def read(self, chunk_size: int) -> bytes:
        # I'm not good with efficient no-copy buffering so if this is
        # wrong or there's a better way to do this let me know! :-)
        to_read = min(chunk_size, self._buffer_size)
        memview = memoryview(self._buffer)
        self._buffer = memview[to_read:].tobytes()
        self._read += to_read
        self._buffer_size -= to_read
        return memview[:to_read].tobytes()

    def tell(self) -> int:
        return self._read


def upload_data(data, remote_path, remote_file_name, mimetype, filesize):
    remote_file_path = '%s/%s' % (remote_path, remote_file_name)

    with GCSObjectStreamUpload(client=client, bucket_name=bucket_name, blob_name=remote_file_path, mimetype=mimetype) as s:
        s.write(data)

    return remote_file_path


def delete_file(path, file_name):
    remote_file_path = '%s/%s' % (path, file_name)
    blob = bucket.blob(remote_file_path)
    blob.delete()


def read_file(path, file_name):
    remote_file_path = '%s/%s' % (path, file_name)
    blob = bucket.blob(remote_file_path)
    fileobj = io.BytesIO()
    blob.download_to_file(fileobj)
    fileobj.seek(0)
    return fileobj.read()


def exist_file(path, file_name):
    remote_file_path = '%s/%s' % (path, file_name)
    blob = bucket.blob(remote_file_path)
    return blob.exists()
