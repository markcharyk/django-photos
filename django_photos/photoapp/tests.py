from django.test import TestCase
from photoapp.models import Album, Photo, Tag
from django.contrib.auth.models import User
from datetime import datetime


class TestAlbum(TestCase):
    fixtures = ['user_fixture.json', ]

    def setUp(self):
        self.u1 = User.objects.create_user('tester', 'tester@domain.com', 'testpass')
        self.a1 = Album.objects.create(
            title="2014 Summer Fun",
            photog=self.u1
        )

    def test_album_gets_data(self):
        self.assertEqual(self.a1.title, "2014 Summer Fun")
        self.assertEqual(self.a1.photog, self.u1)

    def test_album_gets_time(self):
        pass
        # self.assertAlmostEqual(self.a1.created_date, datetime.utcnow())
        # self.assertAlmostEqual(self.a1.modified_date, datetime.utcnow())


class TestPhoto(TestCase):
    fixtures = ['user_fixture.json', ]

    def setUp(self):
        self.u1 = User.objects.create_user('tester', 'tester@domain.com', 'testpass')
        self.a1 = Album.objects.create(
            title="2014 Summer Fun",
            photog=self.u1
        )
        self.p1 = Photo.objects.create(
            photog=self.u1,
            album=self.a1
        )

    def test_blank_caption(self):
        self.assertEqual('', self.p1.caption)
        self.assertEqual(self.p1.photog, self.u1)
        self.assertEqual(self.p1.album, self.a1)
        # self.assertAlmostEqual(self.p1.created_date, datetime.utcnow())
        # self.assertAlmostEqual(self.p1.modified_date, datetime.utcnow())

    def test_with_caption(self):
        p2 = Photo.objects.create(
            caption="Pictured is the eponymous fun",
            photog=self.u1,
            album=self.a1
        )
        self.assertEqual(
            'Pictured is the eponymous fun',
            p2.caption)
        self.assertEqual(p2.photog, self.u1)
        self.assertEqual(p2.album, self.a1)
        # self.assertAlmostEqual(p2.created_date, datetime.utcnow())
        # self.assertAlmostEqual(p2.modified_date, datetime.utcnow())
