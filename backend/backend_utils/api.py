from django.http import HttpResponseRedirect, HttpResponse
from rest_framework import mixins, generics
from rest_framework.response import Response


def response_error(error, status=None):
    header = {"Server": "server"}
    data = {"error": error}

    response = Response(data, headers=header, status=status)
    return response


def response_json(payload, status=None):
    header = {"Server": "server"}
    data = {"payload": payload}

    response = Response(data, headers=header, status=status)
    return response


def response_html(html, status=None):
    header = {"Server": "server"}

    return Response(html, headers=header, status=status)


def response_url(url):
    return HttpResponseRedirect(url)


def response_http(contents, *args, **kwargs):
    return HttpResponse(contents, *args, **kwargs)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class UpdatePUTAPIView(mixins.UpdateModelMixin, generics.GenericAPIView):
    """
    Concrete view for updating a model instance.
    """
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class CreateUpdateAPIView(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    generics.GenericAPIView
):
    """
    Concrete view for creating, retrieving, updating or deleting a model instance.
    """
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class CreateRetrieveAPIView(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    generics.GenericAPIView
):
    """
    Concrete view for creating, retrieving a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ListDestroyAPIView(
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    """
    Concrete view for creating, retrieving, updating or deleting a model instance.
    """
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class CreateListUpdateDestroyAPIView(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView
):
    """
    Concrete view for creating, retrieving, updating or deleting a model instance.
    """
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class CreateListUpdateAPIView(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    generics.GenericAPIView
):
    """
    Concrete view for creating, retrieving, updating a model instance.
    """
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ListUpdateAPIView(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    generics.GenericAPIView
):
    """
    Concrete view for retrieving, updating a model instance.
    """
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
