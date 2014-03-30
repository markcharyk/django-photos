from django.shortcuts import render
from photoapp.models import Album, Photo, Tag
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, permission_required
from photoapp.forms import AlbumForm, PhotoForm, TagForm
from re import sub


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
    other_albums = all_albums.filter(public=True).exclude(photog=request.user)
    albums = users_albums.order_by('-modified_date')
    sec_albums = other_albums.order_by('-modified_date')
    context = {'albums': albums, 'sec_albums': sec_albums, }
    return render(request, 'photoapp/home.html', context)


@login_required
def album_view(request, album_no):
    try:
        alb = Album.objects.get(pk=album_no)
    except Album.DoesNotExist:
        raise Http404("Not here. Plz try again.")
    if alb.photog.pk != request.user.pk and (not alb.public):
        return HttpResponseForbidden("403. Look it up.")
    context = {'album': alb, 'owner': True}
    if alb.photog.pk != request.user.pk:
        context['owner'] = False
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
    if photo.photog.pk != request.user.pk and (not alb.public):
        return HttpResponseForbidden("403. Look it up.")
    context = {'album': alb, 'photo': photo, 'owner': True}
    if photo.photog.pk != request.user.pk:
        context['owner'] = False
    return render(request, 'photoapp/photo.html', context)


@login_required
def tag_view(request, tag_name):
    try:
        tag = Tag.objects.get(title=tag_name.lower())
        user_photos = tag.photos.filter(photog__exact=request.user)
        o_photos = tag.photos.exclude(photog__exact=request.user)
        other_photos = o_photos.filter(album__public=True)
        context = {
            'tag': tag,
            'user_photos': user_photos,
            'other_photos': other_photos
        }
        return render(request, 'photoapp/tag.html', context)
    except Tag.DoesNotExist:
        return render(request, 'photoapp/no_tag.html', {'tag': tag_name})


@permission_required('photoapp.add_album')
def new_album(request):
    if request.method == 'POST':
        input_form = AlbumForm(request.POST)
        if input_form.is_valid():
            new_alb = Album()
            new_title = input_form.cleaned_data['title']
            if len(new_title) > 128:
                new_title = new_title[:127]
            new_alb.title = new_title
            new_alb.photog = request.user
            if input_form.cleaned_data['privacy'] == "True":
                new_alb.public = True
            else:
                new_alb.public = False
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
            partly_cleaned = input_form.cleaned_data['title'].lower()
            new_title = sub(r'\W+', '', partly_cleaned)
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
