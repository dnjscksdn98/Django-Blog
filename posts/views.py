from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Q
from django.views import View

from .models import Post, Author
from .forms import CommentForm, PostForm
from marketing.models import Signup


def get_author(user):
    queryset = Author.objects.filter(user=user)
    if queryset.exists():
        return queryset[0]
    return None


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


def post(request, id):
    post = get_object_or_404(Post, id=id)
    most_recent = Post.objects.order_by('-timestamp')[0:3]
    category_count = get_category_count()
    form = CommentForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.instance.user = request.user
            form.instance.post = post
            form.save()
            post.comment_count += 1
            post.save()
            return redirect(reverse('post-detail', kwargs={
                'id': post.id
            }))

    context = {
        'form': form,
        'post': post,
        'most_recent': most_recent,
        'category_count': category_count
    }
    return render(request, 'post.html', context)


def post_create(request):
    method = 'Create'
    form = PostForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if form.is_valid():
            form.instance.author = get_author(request.user)
            form.save()
            return redirect(reverse('post-detail', kwargs={
                'id': form.instance.id
            }))
    context = {
        'method': method,
        'form': form
    }
    return render(request, 'post_create.html', context)


def post_update(request, id):
    method = 'Update'
    post = get_object_or_404(Post, id=id)
    form = PostForm(
        request.POST or None,
        request.FILES or None,
        instance=post
    )

    if request.method == 'POST':
        if form.is_valid():
            form.instance.author = get_author(request.user)
            form.save()
            return redirect(reverse('post-detail', kwargs={
                'id': form.instance.id
            }))
    context = {
        'method': method,
        'form': form
    }
    return render(request, 'post_create.html', context)


def post_delete(request, id):
    post = get_object_or_404(Post, id=id)
    post.delete()
    return redirect(reverse('post-list'))
