from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view, APIView
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST
from rest_framework import mixins, generics
from rest_framework import permissions
from django.contrib.auth.models import User


from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import renderers
from rest_framework.decorators import action

from .serializers import UserSerializer
from .permissions import IsOwnerOrReadOnly


from .models import Snippet
from .serializers import SnippetSerializer, UserHyperlinkedSerializer, SnippetHyperlinkedSerializer

from rest_framework import viewsets

# function based view


@csrf_exempt
@api_view(['GET', 'POST'])
def snippet_list(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        snippets = Snippet.objects.all()
        serializer = SnippetSerializer(snippets, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = SnippetSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


@csrf_exempt
# this is to ensure that request instance is passed to the view
@api_view(['GET', 'PUT', 'DELETE'])
def snippet_detail(request, pk):
    """
    Retrieve, update or delete a code snippet.
    """
    try:
        snippet = Snippet.objects.get(pk=pk)
    except Snippet.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = SnippetSerializer(snippet)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = SnippetSerializer(snippet, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        snippet.delete()
        return HttpResponse(status=204)


# class based view

class SnippetListView(APIView):
    # here all http methods that are related to a list of instances are defined
    def get(self, request):
        sinppets = Snippet.objects.all()
        serializer = SnippetSerializer(sinppets, many=True)
        return JsonResponse(serializer.data, safe=False)

    def post(self, request):
        serializer = SnippetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=HTTP_400_BAD_REQUEST)


class SnippetDetailView(APIView):
    # here all http methods that are related to a single instance are defined
    def get(self, request, pk):
        try:
            snippet_detail = Snippet.objects.get(pk=pk)
        except Snippet.DoesNotExist:
            return HttpResponse(status=HTTP_404_NOT_FOUND)
        serializer = SnippetSerializer(snippet_detail)
        return JsonResponse(serializer.data)

    def put(self, request, pk):
        try:
            snippet_detail = Snippet.objects.get(pk=pk)
        except Snippet.DoesNotExist:
            return HttpResponse(status=HTTP_404_NOT_FOUND)
        serializer = SnippetSerializer(snippet_detail, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            snippet_detail = Snippet.objects.get(pk=pk)
        except Snippet.DoesNotExist:
            return HttpResponse(status=HTTP_404_NOT_FOUND)
        snippet_detail.delete()
        return HttpResponse(status=HTTP_204_NO_CONTENT)


# using mixins and generic views
class SnippetListView(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      generics.GenericAPIView):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class SnippetDetailView(mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        generics.GenericAPIView):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

# Let's refactor the above code using generic class-based views


class SnippetListView(generics.ListCreateAPIView):
    # here ListCreateAPIView provides defualt implementation for get and post methods, no need of implementing them
    queryset = Snippet.objects.all()
    # serializer_class = SnippetSerializer
    serializer_class = SnippetHyperlinkedSerializer
    # adding permission classes
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    # Associating Snippets with Users
    # this allows us to modify how the instance save is managed, and handle any information that is implicit in the incoming request or requested URL

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    # The create() method of our serializer will now be passed an additional 'owner' field, along with the validated data from the request.


class SnippetDetailView(generics.RetrieveUpdateDestroyAPIView):
    # here RetrieveUpdateDestroyAPIView provides defualt implementation for get, put and delete methods, no need of implementing them
    queryset = Snippet.objects.all()
    # serializer_class = SnippetSerializer
    serializer_class = SnippetHyperlinkedSerializer
    # adding permission classes
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

# READ ONLY VIEWS FOR USER MODEL


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    # serializer_class = UserSerializer
    serializer_class = UserHyperlinkedSerializer


class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    # serializer_class = UserSerializer
    serializer_class = UserHyperlinkedSerializer

# this is api_root view that will be used to generate the root of the api


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'snippets': reverse('snippet-list', request=request, format=format)
    })

# this view is used to highlight the code snippets
#


class SnippetHighlight(generics.GenericAPIView):

    queryset = Snippet.objects.all()
    renderer_classes = [renderers.StaticHTMLRenderer]

    def get(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)


# using viewsets
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """
    queryset = User.objects.all()
    serializer_class = UserHyperlinkedSerializer


class SnippetViewSet(viewsets.ModelViewSet):
    """
    Please be aware that this Note will be desplayed on browsing this api !!

    This ViewSet automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Additionally we also provide an extra `highlight` action.
    """
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
# @action decorator is used to define new custom action in addition to the defualt CRUD provided by the viewSet class

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
