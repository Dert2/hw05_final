from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.core.cache import cache

from .models import Post, Group, Follow
from . import forms

User = get_user_model()


def index(request):
    posts = cache.get('index_page')
    if posts is None:
        posts = Post.objects.all()
        cache.set('index_page', posts, timeout=20)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    form = forms.CommentForm()
    context = {'page': page, 'form': form}
    return render(request, 'index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    form = forms.CommentForm()
    context = {
        'page': page,
        'posts': posts,
        'group': group,
        'form': form
    }
    return render(request, 'group.html', context)


@login_required
def new_post(request):
    form = forms.PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    form = forms.PostForm()
    context = {'form': form}
    return render(request, 'new_post.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = author.following.filter(user=request.user.id).exists()
    context = {
        'author': author,
        'page': page,
        'following': following
    }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author=author)
    comments = post.comments.all()
    form = forms.CommentForm()
    following = author.following.filter(user=request.user.id).exists()
    context = {
        'author': author,
        'post': post,
        'comments': comments,
        'form': form,
        'following': following
    }
    return render(request, 'post.html', context)


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    if post.author.username != request.user.username:
        return redirect(
            'post_view',
            username=request.user.username,
            post_id=post_id
        )
    form = forms.PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect(
            'post_view',
            username=request.user.username,
            post_id=post_id
        )
    context = {
        'user': post.author,
        'post': post,
        'form': form,
        'is_edit': True
    }
    return render(request, 'new_post.html', context)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    form = forms.CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect(
            'post_view',
            username=username,
            post_id=post_id
        )
    context = {'form': form, 'post': post}
    return render(request, 'comments.html', context)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'paginator': paginator,
    }
    return render(request, 'follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('profile', username=username)
