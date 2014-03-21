from django.conf.urls import patterns, url

urlpatterns = patterns(
    'photoapp.views',
    url(
        r'^$',
        'stub_view',
        name='index',
        ),
    url(
        r'^home/$',
        'home_view',
        name='home',
        ),
    url(
        r'^album/(\d+)/$',
        'stub_view',
        name='album_specific',
        ),
    url(
        r'^album/(\d+)/photo/(\d+)/$',
        'stub_view',
        name='photo_specific',
        ),
    url(
        r'^tag/(\d+)/$',
        'stub_view',
        name='tag_specific',
        ),
)
