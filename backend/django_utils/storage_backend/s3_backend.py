from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    location = settings.MEDIAFILES_LOCATION

    def open(self, name, mode='rb'):
        pass

    def save(self, name, content, max_length=None):
        pass

    def path(self, name):
        pass

    def delete(self, name):
        pass

    def exists(self, name):
        pass

    def listdir(self, path):
        pass

    def size(self, name):
        pass

    def get_accessed_time(self, name):
        pass

    def get_created_time(self, name):
        pass

    def get_modified_time(self, name):
        pass


class StaticStorage(S3Boto3Storage):
    location = settings.STATICFILES_LOCATION

    def open(self, name, mode='rb'):
        pass

    def save(self, name, content, max_length=None):
        pass

    def path(self, name):
        pass

    def delete(self, name):
        pass

    def exists(self, name):
        pass

    def listdir(self, path):
        pass

    def size(self, name):
        pass

    def get_accessed_time(self, name):
        pass

    def get_created_time(self, name):
        pass

    def get_modified_time(self, name):
        pass
