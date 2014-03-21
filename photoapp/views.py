from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from photoapp.models import Album, Photo, Tag


def stub_view(request, *args, **kwargs):
    body = "Stub view\n\n"
    if args:
        body += "Args:\n"
        body += "\n".join(["\t%s" % a for a in args])
    if kwargs:
        body += "Kwargs:\n"
        body += "\n".join(["\t%s: %s" % i for i in kwargs.items()])
    return HttpResponse(body, content_type='text/plain')


def home_view(request):
    users_albums = Album.objects.filter(photog=request.user)
    albums = users_albums.order_by('-modified_date')
    context = {'albums': albums}
    return render(request, 'photoapp/home.html', context)
