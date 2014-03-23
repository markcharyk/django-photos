from django.conf.urls import patterns, url

urlpatterns = patterns(
    'photoapp.views',
    url(
        r'^$',
        'index_view',
        name='index',
        ),
    url(
        r'^home/$',
        'home_view',
        name='home',
        ),
    url(
        r'^album/(\d+)/$',
        'album_view',
        name='album_specific',
        ),
    url(
        r'^album/(\d+)/photo/(\d+)/$',
        'photo_view',
        name='photo_specific',
        ),
    url(
        r'^tag/(\w+)/$',
        'tag_view',
        name='tag_specific',
        ),
)
