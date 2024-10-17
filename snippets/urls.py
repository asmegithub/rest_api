from rest_framework.routers import DefaultRouter
from django.urls import path, include
from snippets import views

# we can use viewsets to create views that automatically provide the 'list', 'create', 'retrieve', 'update' and 'destroy' actions as follows:
snippet_list = views.SnippetViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
snippet_detail = views.SnippetViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})
user_list = views.UserViewSet.as_view({
    'get': 'list'
    # No post method here because we are not creating new users manually
})
user_detail = views.UserViewSet.as_view({
    'get': 'retrieve'
    # No put, patch, delete methods here because we are not updating or deleting users manually
})
# then you can use the above views in the urls as we do in the normal function based views:

# But instead of using the above views, we can use router to automatically generate the urls for us:
router = DefaultRouter()
router.register(r'snippets', views.SnippetViewSet, basename='snippet')
router.register(r'users', views.UserViewSet, basename='user')
# and use the router.urls in the urlpatterns

urlpatterns = [
    # routes for function based views
    # path('snippets/', views.snippet_list),
    # path('snippets/<int:pk>/', views.snippet_detail),

    # # routes for class based views
    # path('', views.api_root),
    # path('snippets/<int:pk>/highlight/',
    #      views.SnippetHighlight.as_view(), name="snippet-highlight"),

    # path('snippets/<int:pk>/', views.SnippetDetailView.as_view(),
    #      name='snippet-detail'),
    # path('snippets/', views.SnippetListView.as_view(), name='snippet-list'),
    # path('users/', views.UserListView.as_view(), name='user-list'),
    # path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),

    # # routes for viewsets
    # path('snippets/', snippet_list, name='snippet-list'),
    # path('snippets/<int:pk>/', snippet_detail, name='snippet-detail'),
    # path('users/', user_list, name='user-list'),
    # path('users/<int:pk>/', user_detail, name='user-detail'),

    # routes for viewsets with routers
    path('', include(router.urls))
    # The DefaultRouter class automatically creates the API root view for us, so we can now delete the api_root view.

]
