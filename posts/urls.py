from django.urls import path

from .views import index, blog, search, post, post_create, post_update, post_delete


urlpatterns = [
    path('', index),
    path('blog/', blog, name='post-list'),
    path('search/', search, name='search'),
    path('create/', post_create, name='post-create'),
    path('post/<id>/', post, name='post-detail'),
    path('post/<id>/update/', post_update, name='post-update'),
    path('post/<id>/delete/', post_delete, name='post-delete')
]
