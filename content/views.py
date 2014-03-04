# -*-coding: utf8-*-
from django.shortcuts import render, get_object_or_404, redirect
from django.core.context_processors import csrf
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404

from models import Blog, Comment
from forms import CommentForm
#from core.decorators import ajax_navigation
from tag.models import ArticleTag


def blog_detail(request, slug):
    user = request.user
    
    SLUGS = [
        'slug',
        'drupal_slug',
        'nid',
        'id',
    ]

    for slug_name in SLUGS:
        try:
            if 'id' not in slug_name or slug.isdigit():
                content = Blog.objects.get(**{slug_name: slug})
                break
        except Blog.DoesNotExist:
            continue
    else:
        raise Http404
       
    comments = Comment.objects.filter(blog=content).order_by('-create_time')
    contents = {'content': content, 'comments': comments}
    contents.update(csrf(request))

    if request.method == 'POST' and user.is_authenticated():
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            ip = request.META['REMOTE_ADDR']
            comment_form.save(content, user, ip)
            return redirect(request.META['HTTP_REFERER'])
    else:
        comment_form = CommentForm()
    contents['comment_form'] = comment_form

    return render(request, 'blog/blog_detail.html', contents)


def blog_list(request):
    contents = Blog.objects.all().order_by('-create_time')
    paginator = Paginator(contents, 30)
    page = request.GET.get('p')
    try:
        content = paginator.page(page)
    except PageNotAnInteger:
        content = paginator.page(1)
    except EmptyPage:
        content = paginator.page(paginator.num_pages)
    return render(request, 'blog/blog_list.html', {'content': content})


#@ajax_navigation
def tags(request, tag=None):
    if tag:
        contents = Blog.objects.filter(tags__slug__in=[tag])\
                                    .order_by('-create_time')
    else:
        contents = ArticleTag.objects.all()
        return render(request, 'tag_list.html', {'content': contents})

    if not contents:
        return render(request, 'blog/blog_list.html', {'content': contents})
    paginator = Paginator(contents, 10)

    page = request.GET.get('p')
    try:
        content = paginator.page(page)
    except PageNotAnInteger:
        content = paginator.page(1)
    except EmptyPage:
        content = paginator.page(paginator.num_pages)

    last_date = content[0].create_time.date()
    for c in content:
        content[content.index(c) - 1].__setattr__('linebreack',
                            (c.create_time.date() != last_date))
        if c.create_time.date() != last_date:
            content[content.index(c) - 1].__setattr__('post_date', last_date)
        last_date = c.create_time.date()
    content[-1].__setattr__('post_date', last_date)
    content[-1].__setattr__('linebreack', True)
    return render(request, 'blog/blog_list.html', {'content': content})