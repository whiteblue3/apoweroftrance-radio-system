import sys
import json
import asyncio
import aiohttp
from urllib.parse import urlencode
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


def response_json_payload(payload, status=None):
    header = {"Server": "server"}

    response = Response(payload, headers=header, status=status)
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


def method_permission_classes(classes):
    def decorator(func):
        def decorated_func(self, *args, **kwargs):
            self.permission_classes = classes
            # this call is needed for request permissions
            self.check_permissions(self.request)
            return func(self, *args, **kwargs)
        return decorated_func
    return decorator


def shift(lst):
    tmp = lst[0]

    for i in range(1, len(lst)):
        lst[i-1] = lst[i]

    lst[len(lst) - 1] = tmp


async def request_async(method, url, callback=None, data=None):
    headers = {'content-type': 'application/json'}
    request_data = json.dumps(data)
    async with aiohttp.ClientSession() as session:
        if method == "GET":
            if data is not None:
                query_string = urlencode(request_data)
                request_url = "{0}?{1}".format(url, query_string)
            else:
                request_url = url
            async with session.get(request_url, headers=headers) as resp:
                response = await resp.read()
                if callback is not None:
                    callback(response)
        elif method == "POST":
            async with session.post(url, data=request_data, headers=headers) as resp:
                response = await resp.read()
                if callback is not None:
                    callback(response)


def request_async_threaded(method, url, callback=None, data=None):
    if sys.version_info >= (3, 7):
        tasks = [request_async(method, url, callback, data)]
        asyncio.run(asyncio.wait(tasks))
    else:
        futures = [request_async(method, url, callback, data)]
        # loop = asyncio.get_event_loop()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(asyncio.wait(futures))
        loop.close()


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
