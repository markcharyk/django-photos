from django.shortcuts import render
from django.http import HttpResponse
from photoapp.models import Album, Photo, Tag
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout


def stub_view(request, *args, **kwargs):
    body = "Stub view\n\n"
    if args:
        body += "Args:\n"
        body += "\n".join(["\t%s" % a for a in args])
    if kwargs:
        body += "Kwargs:\n"
        body += "\n".join(["\t%s: %s" % i for i in kwargs.items()])
    return HttpResponse(body, content_type='text/plain')


def index_view(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/photoapp/home')
    return render(request, 'photoapp/index.html', {})


def home_view(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/photoapp')
    users_albums = Album.objects.filter(photog=request.user)
    albums = users_albums.order_by('-modified_date')
    context = {'albums': albums, }
    return render(request, 'photoapp/home.html', context)


def album_view(request, album_no):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/photoapp')
    alb = Album.objects.get(pk=album_no)
    context = {'album': alb, }
    return render(request, 'photoapp/album.html', context)


def photo_view(request, album_no, photo_no):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/photoapp')
    alb = Album.objects.get(pk=album_no)
    photo = Photo.objects.get(pk=photo_no)
    context = {'album': alb, 'photo': photo, }
    return render(request, 'photoapp/photo.html', context)


def tag_view(request, tag_name):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/photoapp')
    try:
        tag = Tag.objects.get(title=tag_name)
        context = {'tag': tag, }
        return render(request, 'photoapp/tag.html', context)
    except Tag.DoesNotExist:
        return render(request, 'photoapp/no_tag.html', {'tag': tag_name})


def login_view(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/photoapp/home')
    context = {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/photoapp/home')
            else:
                return HttpResponse("Your account is disabled")
        else:
            return HttpResponse('Username/password incorrect')
    else:
        return render(request, 'photoapp/login.html', context)


def logout_view(request):
    if request.user.is_authenticated():
        logout(request)
    return HttpResponseRedirect('/photoapp')
