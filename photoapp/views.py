from django.shortcuts import render
from photoapp.models import Album, Photo, Tag
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, permission_required
from photoapp.forms import AlbumForm, PhotoForm, TagForm


# def stub_view(request, *args, **kwargs):
#     body = "Stub view\n\n"
#     if args:
#         body += "Args:\n"
#         body += "\n".join(["\t%s" % a for a in args])
#     if kwargs:
#         body += "Kwargs:\n"
#         body += "\n".join(["\t%s: %s" % i for i in kwargs.items()])
#     return HttpResponse(body, content_type='text/plain')


def index_view(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('home'))
    return render(request, 'photoapp/index.html', {})


@login_required
def home_view(request):
    all_albums = Album.objects.all().prefetch_related()
    users_albums = all_albums.filter(photog=request.user)
    albums = users_albums.order_by('-modified_date')
    context = {'albums': albums, }
    return render(request, 'photoapp/home.html', context)


@login_required
def album_view(request, album_no):
    try:
        alb = Album.objects.get(pk=album_no)
    except Album.DoesNotExist:
        raise Http404("Not here. Plz try again.")
    if alb.photog.pk != request.user.pk:
        return HttpResponseForbidden("403. Look it up.")
    context = {'album': alb, }
    return render(request, 'photoapp/album.html', context)


@login_required
def photo_view(request, album_no, photo_no):
    try:
        alb = Album.objects.get(pk=album_no)
        photo = Photo.objects.get(pk=photo_no)
    except Album.DoesNotExist:
        raise Http404("Not here. Plz try again.")
    except Photo.DoesNotExist:
        raise Http404("Not here. Plz try again.")
    if photo.photog.pk != request.user.pk:
        return HttpResponseForbidden("403. Look it up.")
    context = {'album': alb, 'photo': photo, }
    return render(request, 'photoapp/photo.html', context)


@login_required
def tag_view(request, tag_name):
    try:
        tag = Tag.objects.get(title=tag_name.lower())
        photos = tag.photos.filter(photog__exact=request.user)
        context = {'tag': tag, 'photos': photos}
        return render(request, 'photoapp/tag.html', context)
    except Tag.DoesNotExist:
        return render(request, 'photoapp/no_tag.html', {'tag': tag_name})


@permission_required('photoapp.add_album')
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


@permission_required('photoapp.add_photo')
def new_photo(request, album_no):
    album = Album.objects.get(pk=album_no)
    if album.photog.pk != request.user.pk:
        return HttpResponseForbidden("403. Look it up.")
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


@permission_required('photoapp.add_tag')
def new_tag(request, album_no, photo_no):
    photo = Photo.objects.get(pk=photo_no)
    if photo.photog.pk != request.user.pk:
        return HttpResponseForbidden("403. Look it up.")
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
