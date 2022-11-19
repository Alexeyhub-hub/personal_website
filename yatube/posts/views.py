import django.db.models.query
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Post, Group, User, Follow

NUM_OUTPUT: int = 10
NUM_CHARACTERS: int = 30


@cache_page(20, key_prefix='index_page')
def index(request):
    post_list = Post.objects.select_related('group').all()
    page_number = request.GET.get('page')
    page_obj = get_page_obj(post_list, page_number)
    context = {
        'page_obj': page_obj,
        'view_name': index.__name__
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.select_related('group').filter(
        group=group
    )
    page_number = request.GET.get('page')
    page_obj = get_page_obj(post_list, page_number)
    context = {
        'page_obj': page_obj,
        'title': group.title,
        'description': group.description
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(
            user=request.user, author=author
        ).exists()
    else:
        is_following = False
    if author != request.user:
        user_is_not_author = True
    else:
        user_is_not_author = False
    post_list = Post.objects.select_related('author').filter(
        author=author
    )
    page_number = request.GET.get('page')
    page_obj = get_page_obj(post_list, page_number)
    context = {
        'page_obj': page_obj,
        'posts_number': post_list.count(),
        'author': author,
        'is_profile': True,
        'following': is_following,
        'user_is_not_author': user_is_not_author
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    certain_post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    posts_number = Post.objects.select_related('author').filter(
        author=certain_post.author
    ).count()
    context = {
        'posts_number': posts_number,
        'post': certain_post,
        'title': certain_post.text[:NUM_CHARACTERS],
        'form': form,
        'comments': certain_post.comments.all()
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            author = User.objects.get(pk=request.user.id)
            post = Post(
                text=form.cleaned_data['text'],
                author=author,
                group=form.cleaned_data['group']
            )
            post.save()
            return redirect('posts:profile', author.username)
    form = PostForm()
    context = {
        'form': form,
        'is_edit': False
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = Post.objects.select_related('group').get(pk=post_id)
    if request.user.id is not post.author.id:
        return redirect('posts:post_detail', post_id)
    else:
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=post)
        if request.method == 'POST':
            if form.is_valid():
                post.text = form.cleaned_data['text']
                post.group = form.cleaned_data['group']
                post.save()
                form.save()
                return redirect('posts:post_detail', post_id)
        else:
            group_list = Group.objects.all()
            context = {
                'form': form,
                'group_list': group_list,
                'is_edit': True,
                'post_id': post_id
            }
            return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = User.objects.get(pk=request.user.id)
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.select_related('author').filter(
        author__following__user=request.user
    )
    page_number = request.GET.get('page')
    page_obj = get_page_obj(post_list, page_number)
    context = {
        'page_obj': page_obj,
        'view_name': follow_index.__name__
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    following = get_object_or_404(Follow, user=request.user, author=author)
    following.delete()
    return redirect('posts:profile', username)


def get_page_obj(
        object_list: django.db.models.query.QuerySet,
        page_number: None
) -> django.core.paginator.Page:
    paginator = Paginator(object_list, NUM_OUTPUT)
    return paginator.get_page(page_number)
