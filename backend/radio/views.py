from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
# from .serializers import TMSentenceSerializer, TMGroupSerializer
# from .models import TMSentence, TMGroup
from .api import *


# class TranslateAPIView(CreateRetrieveAPIView):
#     permission_classes = (AllowAny,)
#     serializer_class = TMGroupSerializer
#     renderer_classes = (JSONRenderer,)
#
#     @swagger_auto_schema(operation_summary="TM 추가/편집")
#     @transaction.atomic
#     @method_decorator(ensure_csrf_cookie)
#     def post(self, request, *args, **kwargs):
#         """
#         TM을 추가/편집합니다
#         """
#         serializer = self.serializer_class(data=request.data, context=request)
#         serializer.is_valid(raise_exception=True)
#         data = serializer.save()
#
#         return response_json(data, status.HTTP_200_OK)
#
#     @swagger_auto_schema(operation_summary="TM 가져오기",
#                          query_serializer=TMSentenceSerializer,
#                          responses={'200': TMGroupSerializer})
#     @transaction.atomic
#     @method_decorator(ensure_csrf_cookie)
#     def get(self, request, *args, **kwargs):
#         """
#         TM을 가져옵니다
#         """
#         sentence = request.GET['sentence']
#         language = request.GET['language']
#
#         try:
#             instance_sentence = TMSentence.objects.get(sentence=sentence, language=language)
#             instances = TMGroup.objects.filter(
#                 translated__sentence__exact=instance_sentence.sentence,
#                 translated__language__exact=instance_sentence.language
#             )
#         except TMSentence.DoesNotExist:
#             raise ValidationError(_("TM이 존재하지 않습니다"))
#         except TMGroup.DoesNotExist:
#             raise ValidationError(_("TM이 존재하지 않습니다"))
#
#         serializers = []
#         for instance in instances:
#             serializer = self.serializer_class(instance)
#             data = serializer.fetch(instance)
#             serializers.append(data)
#
#         return response_json(serializers, status.HTTP_200_OK)
