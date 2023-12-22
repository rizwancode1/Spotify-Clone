from django.contrib import admin
from .models import Genre , Album , Artist, Song , Playlist ,Favorite

# Register your models here.

admin.site.register(Favorite)
admin.site.register(Playlist)
admin.site.register(Genre)
admin.site.register(Album)
admin.site.register(Artist)
admin.site.register(Song)