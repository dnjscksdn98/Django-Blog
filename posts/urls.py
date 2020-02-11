from django.urls import path

from .views import IndexView, SearchView, PostListView, PostDetailView, PostCreateView, PostUpdateView, PostDeleteView
from marketing.views import email_list_signup


urlpatterns = [
    path('', IndexView.as_view(), name='home'),
    path('blog/', PostListView.as_view(), name='post-list'),
    path('search/', SearchView.as_view(), name='search'),
    path('create/', PostCreateView.as_view(), name='post-create'),
    path('post/<pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/<pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('email_list_signup/', email_list_signup, name='email-list-signup')
]
