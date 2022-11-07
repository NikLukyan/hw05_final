from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def my_paginator(request, list_name, num_on_page):
    paginator = Paginator(list_name, num_on_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


@cache_page(20, key_prefix='index_page')
def index(request):
    """Function index make selection of 10 posts,
    create content and return home page (index.html) with context
    """
    post_list = Post.objects.select_related("author", "group")
    context = {
        'page_obj': my_paginator(request, post_list, settings.POSTS_PER_PAGE),
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """
    Function group_posts collect content and create page (group_list.html)
    where display posts in group <slug>. Else, return 404 page.
    """
    group_post = get_object_or_404(Group, slug=slug)
    posts = group_post.posts.select_related('author', 'group')
    context = {
        'group': group_post,
        'page_obj': my_paginator(request, posts, settings.POSTS_PER_GROUP),
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Function profile collect content and create page (profile.html)
    where display posts by author <username>. Else, return 404 page.
    """
    auth = get_object_or_404(User, username=username)
    auth_post_list = auth.posts.select_related('author', 'group')
    is_following = (
        request.user.is_authenticated
        and Follow.objects.filter(user=request.user, author=auth).exists()
    )
    context = {
        'page_obj': my_paginator(
            request, auth_post_list, settings.POSTS_PER_PAGE
        ),
        'author': auth,
        'following': is_following,
        'user': request.user,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """
    Function post_detail collect content and create
    page (post_detail.html) where display detail
    information of post with num of post_id.
    """
    post_id_detail = get_object_or_404(Post, pk=post_id)
    form = CommentForm()
    comments_list = post_id_detail.comments.all()
    context = {
        'post': post_id_detail,
        'form': form,
        'comments': comments_list,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """
    Function create new post. It's available only
    for autenficated users.
    """
    form = PostForm(request.POST or None)
    if request.method == 'POST':
        form = PostForm(request.POST or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', post.author)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    """
    Function edit post. It's available only
    for author of post.
    """
    unique_post = get_object_or_404(Post, pk=post_id)
    if unique_post.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=unique_post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'is_edit': True,
        'post': unique_post,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    """
    Function create new comment for post.
    It's available only for autenficated users.
    """
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Function displays the posts of authors
    to which the current user is subscribed."""
    post_list = Post.objects.filter(author__following__user=request.user)
    context = {
        'page_obj': my_paginator(request, post_list, settings.POSTS_PER_PAGE),
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Function help to subscribe the user to author."""
    auth = get_object_or_404(User, username=username)
    if not (
        Follow.objects.filter(user=request.user, author=auth).exists()
        and auth != request.user
    ):
        Follow.objects.create(user=request.user, author=auth)
    return redirect('posts:profile', auth)


@login_required
def profile_unfollow(request, username):
    """Function help to unsubscribe the user to author."""
    author = get_object_or_404(User, username=username)
    if Follow.objects.filter(user=request.user, author=author).exists():
        Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:follow_index')
