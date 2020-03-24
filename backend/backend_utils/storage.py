import fleep
import uuid
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ValidationError

from .storage_driver import gcloud as driver
# from .storage_driver import s3 as driver


def get_extension(filename):
    return str(filename).split('.')[-1]


def upload_file(request, filefield, target_path, valid_mimetype):
    """
    파일을 업로드

    :param request:
    :param filefield:
    :param target_path: media 디렉토리 밑의 경로를 입력한다
    :return: 업로드된 파일의 경로.
    """
    filepath = []
    for f in request.FILES.getlist(filefield):
        filename = f.name
        filebody = f

        extension = get_extension(filename)

        # make unique filename
        uid = str(uuid.uuid1())
        uniquename = uid.replace('-', '') + "." + extension

        data = filebody.read()
        info = fleep.get(data)
        is_valid = False
        for mimetype in valid_mimetype:
            if info.mime_matches(mimetype) is True:
                is_valid = True

        if is_valid is False:
            raise ValidationError(_('Not a image or Invalid format'))

        remote_file_path = driver.upload_data(data, target_path, uniquename, filebody.content_type, filebody.size)

        if remote_file_path is not None:
            filepath.append(remote_file_path)
    if len(filepath) < 1:
        return None
    return filepath


def delete_file(target_path, filename):
    """
    파일을 삭제한다

    :param target_path: media 디렉토리 밑의 경로를 입력한다
    :param filename:
    :return:
    """
    driver.delete_file(target_path, filename)


def get_file(target_path, filename):
    """
    파일을 가져온다.

    :param target_path: media 디렉토리 밑의 경로를 입력한다.
    :param filename:
    :return: 바이너리 포멧의 실제 파일 데이터
    """
    return driver.read_file(target_path, filename)


def exist_file(target_path, filename):
    """
    파일이 존재하는지 확인한다.

    :param target_path:  media 디렉토리 밑의 경로를 입력한다.
    :param filename:
    :return: 파일이 존재하면 True, 아니면 False
    """
    return driver.exist_file(target_path, filename)
