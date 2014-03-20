from django.contrib import admin
from photoapp.models import Album, Photo, Tag
from django.core.urlresolvers import reverse


class AlbumAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'created_date', 'album_link')

    def album_link(self, album):
        url = reverse('admin:auth_user_change', args=(album.id,))
        name = album.photog
        return '<a href="%s">%s</a>' % (url, name)

    album_link.allow_tags = True
    album_link.short_description = "Album"


class TagInlineAdmin(admin.TabularInline):
    model = Tag.photos.through
    extra = 1


class PhotoAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'created_date', 'photo_link')
    inlines = [TagInlineAdmin, ]

    def photo_link(self, photo):
        url = reverse('admin:auth_user_change', args=(photo.id,))
        name = photo.photog
        return '<a href="%s">%s</a>' % (url, name)

    photo_link.allow_tags = True
    photo_link.short_description = "Photo"


class TagAdmin(admin.ModelAdmin):
    list_display = ('__unicode__',)
    exclude = ('photos', )


admin.site.register(Album, AlbumAdmin)
admin.site.register(Photo, PhotoAdmin)
admin.site.register(Tag, TagAdmin)
