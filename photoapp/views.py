from django.shortcuts import render
from django.http import HttpResponse
from photoapp.models import Album, Photo, Tag
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from photoapp.forms import AlbumForm, PhotoForm, TagForm


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
        return HttpResponseRedirect(reverse('home'))
    return render(request, 'photoapp/index.html', {})


def home_view(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('index'))
    all_albums = Album.objects.all().prefetch_related()
    users_albums = all_albums.filter(photog=request.user)
    albums = users_albums.order_by('-modified_date')
    context = {'albums': albums, }
    return render(request, 'photoapp/home.html', context)
    # all = Album.objects.all().select_related('photos')
    # all = Album.objects.all().prefetch_related()


def album_view(request, album_no):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('index'))
    alb = Album.objects.get(pk=album_no)
    context = {'album': alb, }
    return render(request, 'photoapp/album.html', context)


def photo_view(request, album_no, photo_no):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('index'))
    alb = Album.objects.get(pk=album_no)
    photo = Photo.objects.get(pk=photo_no)
    context = {'album': alb, 'photo': photo, }
    return render(request, 'photoapp/photo.html', context)


def tag_view(request, tag_name):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('index'))
    try:
        tag = Tag.objects.get(title=tag_name.lower())
        context = {'tag': tag, }
        return render(request, 'photoapp/tag.html', context)
    except Tag.DoesNotExist:
        return render(request, 'photoapp/no_tag.html', {'tag': tag_name})


# def login_view(request):
#     if request.user.is_authenticated():
#         return HttpResponseRedirect(reverse('home'))
#     context = {}
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#         user = authenticate(username=username, password=password)
#         if user is not None:
#             if user.is_active:
#                 login(request, user)
#                 return HttpResponseRedirect(reverse('home'))
#             else:
#                 return HttpResponse("Your account is disabled")
#         else:
#             return HttpResponse('Username/password incorrect')
#     else:
#         return render(request, 'photoapp/login.html', context)
#         # django.contrib.auth.views.login


# def logout_view(request):
#     if request.user.is_authenticated():
#         logout(request)
#     return HttpResponseRedirect(reverse('index'))


@login_required
def new_album(request):
    if request.method == 'POST':
        input_form = AlbumForm(request.POST)
        if input_form.is_valid():
            new_alb = Album()
            new_alb.title = input_form.cleaned_data['title']
            new_alb.photog = request.user
            new_alb.save()
            return HttpResponseRedirect(reverse('home'))
    form = AlbumForm()
    return render(request, 'photoapp/new_album.html', {'form': form})


@login_required
def new_photo(request, album_no):
    # import pdb; pdb.set_trace()
    album = Album.objects.get(pk=album_no)
    if request.method == 'POST':
        input_form = PhotoForm(request.POST, request.FILES)
        if input_form.is_valid():
            new_photo = Photo(image=request.FILES['image'])
            new_photo.caption = input_form.cleaned_data['caption']
            new_photo.photog = request.user
            new_photo.album = album
            new_photo.save()
            return HttpResponseRedirect(reverse(
                'album_specific',
                args=(album_no, )
            ))
    form = PhotoForm()
    return render(
        request,
        'photoapp/new_photo.html',
        {'form': form, 'album': album}
    )


@login_required
def new_tag(request, album_no, photo_no):
    photo = Photo.objects.get(pk=photo_no)
    if request.method == 'POST':
        input_form = TagForm(request.POST)
        if input_form.is_valid():
            new_title = input_form.cleaned_data['title'].lower()
            try:
                old_tag = Tag.objects.get(title=new_title)
                old_tag.photos.add(photo)
                old_tag.save()
            except Tag.DoesNotExist:
                new_tag = Tag()
                new_tag.title = new_title
                new_tag.save()
                new_tag.photos.add(photo)
                new_tag.save()
            return HttpResponseRedirect(reverse(
                'photo_specific',
                args=(album_no, photo_no)
            ))
    form = TagForm()
    return render(request, 'photoapp/add_tag.html', {
        'form': form,
        'album_no': album_no,
        'photo': photo
    })
