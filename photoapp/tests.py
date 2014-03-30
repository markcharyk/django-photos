from django.test import TestCase
from photoapp.models import Album, Photo, Tag
from photoapp.admin import AlbumAdmin, PhotoAdmin
from django.contrib.auth.models import User
from django.test import Client
from django.contrib.admin.sites import AdminSite
from django_photos.settings import Base


class TestPhoto(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(
            'tester',
            'tester@domain.com',
            'testpass'
            )
        self.a1 = Album.objects.create(
            title="2014 Summer Fun",
            photog=self.u1,
            public=True
        )
        self.p1 = Photo.objects.create(
            photog=self.u1,
            album=self.a1
        )
        self.p2 = Photo.objects.create(
            caption="Pictured is the eponymous fun",
            photog=self.u1,
            album=self.a1
        )

    def test_unicode(self):
        self.assertIn(u'Photo', unicode(self.p1))
        self.assertIn(u'Photo', unicode(self.p2))
        try:
            int(unicode(self.p1)[-1])
            int(unicode(self.p2)[-1])
        except TypeError:
            self.fail("Not a valid type")

    def test_blank_caption(self):
        expected = 'Uncaptioned'
        actual = self.p1.caption_rep()
        self.assertEqual(expected, actual)

    def test_with_caption(self):
        expected = 'Pictured is the eponymous fun'
        actual = self.p2.caption_rep()
        self.assertEqual(expected, actual)


class TestAlbumAdmin(TestCase):

    def setUp(self):
        self.u1 = User.objects.create_user(
            'tester',
            'tester@domain.com',
            'testpass'
            )
        self.a1 = Album.objects.create(
            title="2014 Summer Fun",
            photog=self.u1,
            public=True
        )
        self.site = AdminSite()
        self.aa = AlbumAdmin(Album, self.site)

    def test_link(self):
        expected = '/">tester'
        actual = self.aa.album_link(self.a1)
        self.assertIn(expected, actual)


class TestPhotoAdmin(TestCase):
    def setUp(self):
            self.u1 = User.objects.create_user(
                'tester',
                'tester@domain.com',
                'testpass'
                )
            self.a1 = Album.objects.create(
                title="2014 Summer Fun",
                photog=self.u1,
                public=True
            )
            self.p1 = Photo.objects.create(
                photog=self.u1,
                album=self.a1
            )
            self.site = AdminSite()
            self.pa = PhotoAdmin(Photo, self.site)

    def test_link(self):
        expected = '/">tester'
        actual = self.pa.photo_link(self.p1)
        self.assertIn(expected, actual)


class TestViews(TestCase):
    fixtures = ['photo_test_fixtures.json', ]

    def setUp(self):
        self.client = Client()
        self.client.login(username='admin', password='admin')

    def tearDown(self):
        self.client.logout()

    def test_home_view(self):
        resp = self.client.get('/photoapp/home', follow=True)
        self.assertContains(resp, 'Albums')
        self.assertContains(resp, '2014 Summer Fun')
        self.assertContains(resp, 'Admin Stuff')
        self.assertContains(resp, 'Not the Stuff of Admins')
        self.assertNotContains(resp, 'Login here')

    def test_redirect_home(self):
        resp = self.client.get('/photoapp/', follow=True)
        self.assertContains(resp, 'Albums')
        self.assertContains(resp, '2014 Summer Fun')
        self.assertContains(resp, 'Admin Stuff')
        self.assertContains(resp, 'Not the Stuff of Admins')
        self.assertNotContains(resp, '<b>Log in')

    def test_home_public_private(self):
        self.client.logout()
        self.client.login(username='thor', password='lokisbro')
        resp = self.client.get('/photoapp/home', follow=True)
        self.assertContains(resp, 'Not the Stuff of Admins')
        self.assertContains(resp, '2014 Summer Fun')
        self.assertNotContains(resp, 'Admin Stuff')

    def test_logged_out(self):
        self.client.logout()
        resp = self.client.get('/photoapp/', follow=True)
        self.assertContains(resp, '<b>Log in')
        self.assertNotContains(resp, 'Albums')

    def test_logged_out_redirect(self):
        self.client.logout()
        expected = '<form method="post" action="/accounts/login/">'
        resp = self.client.get('/photoapp/home', follow=True)
        self.assertContains(resp, expected)
        self.assertNotContains(resp, 'Albums')
        resp = self.client.get('/photoapp/album/2', follow=True)
        self.assertContains(resp, expected)
        self.assertNotContains(resp, 'Albums')
        resp = self.client.get('/photoapp/album/2/photo/1', follow=True)
        self.assertContains(resp, expected)
        self.assertNotContains(resp, 'Albums')
        resp = self.client.get('/photoapp/tag/screenshot', follow=True)
        self.assertContains(resp, expected)
        self.assertNotContains(resp, 'Albums')

    def test_album_view(self):
        resp = self.client.get('/photoapp/album/2', follow=True)
        self.assertContains(resp, 'Admin Stuff')
        self.assertNotContains(resp, 'Not the Stuff of Admins')
        self.assertNotContains(resp, 'Summer Fun')

    def test_invalid_album(self):
        resp = self.client.get('/photoapp/album/32', follow=True)
        self.assertEqual(resp.status_code, 404)

    def test_album_forbidden(self):
        self.client.logout()
        self.client.login(username='thor', password='lokisbro')
        resp = self.client.get('/photoapp/album/2', follow=True)
        self.assertEqual(resp.status_code, 403)

    def test_album_not_forbidden(self):
        self.client.logout()
        self.client.login(username='thor', password='lokisbro')
        resp = self.client.get('/photoapp/album/1', follow=True)
        self.assertContains(resp, 'Summer Fun')
        self.assertEqual(resp.status_code, 200)

    def test_photo_view(self):
        resp = self.client.get('/photoapp/album/2/photo/1', follow=True)
        self.assertContains(resp, 'An admin photo')
        self.assertNotContains(resp, 'Not the photo of an admin')

    def test_invalid_photo(self):
        resp = self.client.get('/hotoapp/album/2/photo/15', follow=True)
        self.assertEqual(resp.status_code, 404)

    def test_photo_forbidden(self):
        self.client.logout()
        self.client.login(username='thor', password='lokisbro')
        resp = self.client.get('/photoapp/album/2/photo/1', follow=True)
        self.assertEqual(resp.status_code, 403)

    def test_photo_not_forbidden(self):
        self.client.logout()
        self.client.login(username='thor', password='lokisbro')
        resp = self.client.get('/photoapp/album/1/photo/3', follow=True)
        self.assertContains(resp, "Admin&#39;s public photo")

    def test_tag_view(self):
        resp = self.client.get('/photoapp/tag/testtag', follow=True)
        self.assertContains(resp, 'album/3/photo/2')
        self.assertContains(resp, 'album/2/photo/1')

    def test_empty_tag(self):
        resp = self.client.get('/photoapp/tag/notag', follow=True)
        self.assertContains(resp, 'No photos tagged')
        self.assertNotContains(resp, 'album/')

    def test_tag_public_private(self):
        self.client.logout()
        self.client.login(username='thor', password='lokisbro')
        resp = self.client.get('/photoapp/tag/publicprivate', follow=True)
        self.assertContains(resp, 'photo/3')
        self.assertNotContains(resp, 'photo/1')

    def test_new_album_get(self):
        resp = self.client.get('/photoapp/new_album', follow=True)
        self.assertContains(resp, 'Create Album')

    def test_new_album_post(self):
        self.client.post(
            '/photoapp/new_album/',
            {'title': 'Make a New Album', 'privacy': "True"}
        )
        newbie = Album.objects.get(title='Make a New Album')
        self.assertIsNotNone(newbie)

    def test_new_photo_get(self):
        resp = self.client.get('/photoapp/album/1/new_photo', follow=True)
        self.assertContains(resp, 'Add Photo')

    def test_new_photo_post(self):
        with open('%s/2014/03/19/HAIKUTE.png' % Base.MEDIA_ROOT) as im:
            self.client.post(
                '/photoapp/album/1/new_photo/',
                {'caption': 'Haikute ss', 'image': im}
            )
        newbie = Photo.objects.get(caption='Haikute ss')
        self.assertIsNotNone(newbie)

    def test_new_tag_get(self):
        resp = self.client.get(
            '/photoapp/album/2/photo/1/new_tag',
            follow=True
        )
        self.assertContains(resp, 'Add Tag')

    def test_new_tag_post(self):
        self.client.post(
            '/photoapp/album/2/photo/1/new_tag/',
            {'title': 'boomerdog'}
        )
        newbie = Tag.objects.get(title='boomerdog')
        self.assertIsNotNone(newbie)

    def test_extant_tag_post(self):
        self.client.logout()
        self.client.login(username='thor', password='lokisbro')
        self.client.post(
            '/photoapp/album/3/photo/2/new_tag/',
            {'title': 'testtagtwo'}
        )
        photos = Photo.objects.filter(tag__title='testtagtwo')
        act_captions = [photos[0].caption, photos[1].caption]
        exp_captions = ['An admin photo', 'Not the photo of an admin', ]
        for cap in act_captions:
            self.assertIn(cap, exp_captions)

    def test_non_alnum_tag(self):
        self.client.post(
            '/photoapp/album/2/photo/1/new_tag/',
            {'title': 'tag_with_weird0$&@^'}
        )
        newbie = Tag.objects.get(title='tag_with_weird0')
        self.assertIsNotNone(newbie)
