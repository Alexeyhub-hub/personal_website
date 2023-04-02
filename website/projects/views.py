import django.db.models.query
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

from .forms import PostForm
from .models import Post, User

NUM_OUTPUT: int = 10
NUM_CHARACTERS: int = 30


def index(request):
    return render(request, 'about/author.html')


@cache_page(20, key_prefix='creativity_page')
def creativity(request):
    post_list = Post.objects.all()
    page_number = request.GET.get('page')
    page_obj = get_page_obj(post_list, page_number)
    context = {
        'page_obj': page_obj,
        'view_name': creativity.__name__
    }
    return render(request, 'projects/index.html', context)


def post_detail(request, post_id):
    certain_post = get_object_or_404(Post, pk=post_id)
    posts_number = Post.objects.select_related('author').filter(
        author=certain_post.author
    ).count()
    context = {
        'posts_number': posts_number,
        'post': certain_post,
        'title': certain_post.text[:NUM_CHARACTERS],
    }
    return render(request, 'projects/post_detail.html', context)


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            author = User.objects.get(pk=request.user.id)
            post = Post(
                text=form.cleaned_data['text'],
                author=author,
            )
            post.save()
            return redirect('projects:profile', author.username)
    form = PostForm()
    context = {
        'form': form,
        'is_edit': False
    }
    return render(request, 'projects/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = Post.objects.get(pk=post_id)
    if request.user.id is not post.author.id:
        return redirect('projects:post_detail', post_id)
    else:
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=post)
        if request.method == 'POST':
            if form.is_valid():
                post.text = form.cleaned_data['text']
                post.save()
                form.save()
                return redirect('projects:post_detail', post_id)
        else:
            context = {
                'form': form,
                'is_edit': True,
                'post_id': post_id
            }
            return render(request, 'projects/create_post.html', context)


def get_page_obj(
        object_list: django.db.models.query.QuerySet,
        page_number: None
) -> django.core.paginator.Page:
    paginator = Paginator(object_list, NUM_OUTPUT)
    return paginator.get_page(page_number)
