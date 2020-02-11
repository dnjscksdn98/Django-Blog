from django.db import models
from django.conf import settings
from django.urls import reverse

from tinymce.models import HTMLField
# from django.contrib.auth import get_user_model


# User = get_user_model()


class PostView(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class Comment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    post = models.ForeignKey(
        'Post', related_name='comments', on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class Author(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_image = models.ImageField()

    def __str__(self):
        return self.user.username


class Category(models.Model):
    title = models.CharField(max_length=20)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Categories'


class Post(models.Model):
    title = models.CharField(max_length=100)
    overview = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    # comment_count = models.IntegerField(default=0)
    # view_count = models.IntegerField(default=0)
    author = models.ForeignKey('Author', on_delete=models.CASCADE)
    thumbnail = models.ImageField()
    category = models.ManyToManyField(Category)
    featured = models.BooleanField(default=False)
    content = HTMLField()
    previous_post = models.ForeignKey(
        'self', related_name='previous', on_delete=models.SET_NULL, blank=True, null=True)
    next_post = models.ForeignKey(
        'self', related_name='next', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={
            'pk': self.pk
        })

    def get_update_url(self):
        return reverse('post-update', kwargs={
            'pk': self.pk
        })

    def get_delete_url(self):
        return reverse('post-delete', kwargs={
            'pk': self.pk
        })

    @property
    def get_comments(self):
        return self.comments.all().order_by('-timestamp')

    @property
    def view_count(self):
        return PostView.objects.filter(post=self).count()

    @property
    def comment_count(self):
        return Comment.objects.filter(post=self).count()
