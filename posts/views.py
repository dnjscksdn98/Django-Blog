from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Q

from .models import Post
from marketing.models import Signup


def index(request):
    featured = Post.objects.filter(featured=True)
    latest = Post.objects.order_by('-timestamp')[0:3]

    if request.method == 'POST':
        email = request.POST.get('email')
        new_signup = Signup(email=email)
        new_signup.save()

    context = {
        'object_list': featured,
        'latest': latest
    }
    return render(request, 'index.html', context)


def get_category_count():
    # only returns the category object
    queryset = Post.objects.values(
        'category__title').annotate(Count('category__title'))
    return queryset


def search(request):
    queryset = Post.objects.all()
    query = request.GET.get('q')
    if query:
        # if title or overview contains query
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(overview__icontains=query)
        ).distinct()  # just get one queryset

    context = {
        'queryset': queryset
    }
    return render(request, 'search_result.html', context)


def blog(request):
    category_count = get_category_count()
    most_recent = Post.objects.order_by('-timestamp')[0:3]
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 4)
    page_request_var = 'page'
    # return the current page
    page = request.GET.get(page_request_var)

    try:
        # retrieve the current page posts
        paginated_queryset = paginator.page(page)

    except PageNotAnInteger:
        # retrieve the first page posts
        paginated_queryset = paginator.page(1)

    except EmptyPage:
        # retrieve the last page posts
        paginated_queryset = paginator.page(paginator.num_pages)

    context = {
        'queryset': paginated_queryset,
        'most_recent': most_recent,
        'page_request_var': page_request_var,
        'category_count': category_count
    }
    return render(request, 'blog.html', context)


def post(request, slug):
    return render(request, 'post.html', {})
