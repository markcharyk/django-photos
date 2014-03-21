from django.test import TestCase
from photoapp.models import Album, Photo
from photoapp.admin import AlbumAdmin, PhotoAdmin
from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite


class TestPhoto(TestCase):
    fixtures = ['user_fixture.json', ]

    def setUp(self):
        self.u1 = User.objects.create_user(
            'tester',
            'tester@domain.com',
            'testpass'
            )
        self.a1 = Album.objects.create(
            title="2014 Summer Fun",
            photog=self.u1
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
    fixtures = ['user_fixture.json', ]

    def setUp(self):
        self.u1 = User.objects.create_user(
            'tester',
            'tester@domain.com',
            'testpass'
            )
        self.a1 = Album.objects.create(
            title="2014 Summer Fun",
            photog=self.u1
        )
        self.site = AdminSite()
        self.aa = AlbumAdmin(Album, self.site)

    def test_link(self):
        expected = '/">tester'
        actual = self.aa.album_link(self.a1)
        self.assertIn(expected, actual)


class TestPhotoAdmin(TestCase):
    fixtures = ['user_fixture.json', ]

    def setUp(self):
        self.u1 = User.objects.create_user(
            'tester',
            'tester@domain.com',
            'testpass'
            )
        self.a1 = Album.objects.create(
            title="2014 Summer Fun",
            photog=self.u1
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


class TestUrlViews(TestCase):
    fixtures = ['user_fixture.json', ]

    def setUp(self):
        photog1 = User.objects.get(pk=1)
        photog2 = User.objects.get(pk=2)
        # log in photog1
        for count in range(1, 7):
            title = "Album %d" % count
            if count % 2 == 1:
                album = Album(
                    title=title,
                    photog=photog1,
                    )
            else:
                album = Album(
                    title=title,
                    photog=photog2,
                    )
            album.save()

    def test_only_show_own_(self):
        resp = self.client.get('/home/')
        self.assertContains(resp, 'Albums')
        for count in range(1, 7):
            title = "Album %d" % count
            if count % 2 == 1:
                self.assertContains(resp, title)
            else:
                self.assertNotContains(resp, title)
