from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Q
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView

from .models import Post, Author, PostView
from .forms import CommentForm, PostForm
from marketing.models import Signup
from marketing.forms import EmailSignupForm


def get_author(user):
    queryset = Author.objects.filter(user=user)
    if queryset.exists():
        return queryset[0]
    return None


def get_category_count():
    # only returns the category object
    queryset = Post.objects.values(
        'category__title').annotate(Count('category__title'))
    return queryset


class IndexView(View):
    form = EmailSignupForm()

    def get(self, request, *args, **kwargs):
        featured = Post.objects.filter(featured=True)
        latest = Post.objects.order_by('-timestamp')[0:3]
        context = {
            'object_list': featured,
            'latest': latest,
            'form': self.form
        }
        return render(self.request, 'index.html', context)

    def post(self, request, *args, **kwargs):
        email = self.request.POST.get('email')
        new_signup = Signup(email=email)
        new_signup.save()
        messages.info(self.request, 'Successfully subscribed.')
        return redirect('home')


'''
def index(request):
    featured = Post.objects.filter(featured=True)
    latest = Post.objects.order_by('-timestamp')[0:3]
    form = EmailSignupForm()

    if request.method == 'POST':
        email = request.POST.get('email')
        new_signup = Signup(email=email)
        new_signup.save()

    context = {
        'object_list': featured,
        'latest': latest,
        'form': form
    }
    return render(request, 'index.html', context)
'''


class SearchView(View):
    def get(self, request, *args, **kwargs):
        queryset = Post.objects.all()
        query = request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(overview__icontains=query)
            ).distinct()
        context = {
            'queryset': queryset
        }
        return render(request, 'search_result.html', context)


'''
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
'''


class PostListView(ListView):
    form = EmailSignupForm()
    model = Post
    template_name = 'blog.html'
    context_object_name = 'queryset'
    paginate_by = 4

    def get_context_data(self, **kwargs):
        category_count = get_category_count()
        most_recent = Post.objects.order_by('-timestamp')[0:3]
        context = super().get_context_data(**kwargs)
        context['category_count'] = category_count
        context['most_recent'] = most_recent
        context['page_request_var'] = 'page'
        context['form'] = self.form
        return context


'''
def blog(request):
    form = EmailSignupForm()
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
        'category_count': category_count,
        'form': form
    }
    return render(request, 'blog.html', context)
'''


class PostDetailView(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'
    form = CommentForm()

    def get_object(self):
        obj = super().get_object()
        if self.request.user.is_authenticated:
            PostView.objects.get_or_create(user=self.request.user, post=obj)
        return obj

    def get_context_data(self, **kwargs):
        category_count = get_category_count()
        most_recent = Post.objects.order_by('-timestamp')[0:3]
        context = super().get_context_data(**kwargs)
        context['most_recent'] = most_recent
        context['category_count'] = category_count
        context['form'] = self.form
        return context

    def post(self, request, *args, **kwargs):
        form = CommentForm(request.POST)
        if form.is_valid():
            post = self.get_object()
            form.instance.user = self.request.user
            form.instance.post = post
            form.save()
            return redirect(reverse('post-detail', kwargs={
                'pk': post.pk
            }))


'''
def post(request, id):
    post = get_object_or_404(Post, id=id)
    most_recent = Post.objects.order_by('-timestamp')[0:3]
    category_count = get_category_count()
    form = CommentForm(request.POST or None)

    if request.user.is_authenticated:
        PostView.objects.get_or_create(user=request.user, post=post)

    if request.method == 'POST':
        if form.is_valid():
            form.instance.user = request.user
            form.instance.post = post
            form.save()
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
'''


class PostCreateView(CreateView):
    model = Post
    template_name = 'post_create.html'
    form_class = PostForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['method'] = 'Create'
        return context

    def form_valid(self, form):
        form.instance.author = get_author(self.request.user)
        form.save()
        return redirect(reverse('post-detail', kwargs={
            'pk': form.instance.pk
        }))


'''
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
'''


class PostUpdateView(UpdateView):
    model = Post
    template_name = 'post_create.html'
    form_class = PostForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['method'] = 'Update'
        return context

    def form_valid(self, form):
        form.instance.author = get_author(self.request.user)
        form.save()
        return redirect(reverse('post-detail', kwargs={
            'pk': form.instance.pk
        }))


'''
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
'''


class PostDeleteView(DeleteView):
    model = Post
    success_url = '/blog'
    template_name = 'post_confirm_delete.html'


'''
def post_delete(request, id):
    post = get_object_or_404(Post, id=id)
    post.delete()
    return redirect(reverse('post-list'))
'''
