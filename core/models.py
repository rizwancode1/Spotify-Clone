import os
import uuid
import mutagen # for song metadata 
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db.models import Q
from django.core.files import File
from PIL import Image 
from io import BytesIO
from django.urls import reverse








def thumbnail_path(instance, filename):
    # Generate a unique filename for the thumbnail
    ext = filename.split('.')[-1]
    filename = f"thumbnail_{uuid.uuid4()}.{ext}"
    return os.path.join('thumbnails/', filename)

def audio_file_path(instance, filename):
    # Generate a unique filename for the uploaded audio file
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('audio/', filename)


def make_thumbnail(self, image, size =(300, 300)):
        img = Image.open(image)
        img.convert('RGB')
        img.thumbnail(size)
        thum_io = BytesIO()
        img.save(thum_io, 'JPEG', quality=85)
        thumbnail = File(thum_io, name=image.name)
        return thumbnail
        




class Playlist(models.Model):
    image = models.ImageField(blank=True, null=True, upload_to='Playlist_images/' )
    thumbnail = models.ImageField(blank=True, null=True,  upload_to=thumbnail_path)
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    songs = models.ManyToManyField('Song', related_name='playlists')
    created_at = models.DateTimeField( auto_now_add=True)



    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.name

    def add_song(self, song):
        self.songs.add(song)

    def remove_song(self, song):
        self.songs.remove(song)

    def make_thumbnail(self, image, size =(300, 300)):
        img = Image.open(image)
        img.convert('RGB')
        img.thumbnail(size)
        thum_io = BytesIO()
        img.save(thum_io, 'JPEG', quality=85)
        thumbnail = File(thum_io, name=image.name)
        return thumbnail


    def get_thumbnail(self):
        if self.thumbnail:
            return self.thumbnail.url
        else:
            if self.image:
                self.thumbnail = self.make_thumbnail(self.image)
                self.save()
                return self.thumbnail.url
            else:
                return 'https://via.placeholder.com/640x360.jpg'




class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Artist(models.Model):
    name = models.CharField(max_length=200)


    def __str__(self):
        return self.name

class Album(models.Model):
    title = models.CharField(max_length=200)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    release_date = models.DateField()
    image = models.ImageField(upload_to='album_images/')
    thumbnail = models.ImageField(blank=True, null=True ,upload_to=thumbnail_path)

    def __str__(self):
        return self.title

    @property
    def name(self):
        return self.title   ### name = title 
    
    

    def get_thumbnail(self):
        if self.thumbnail:
            return self.thumbnail.url
        else:
            if self.image:
                self.thumbnail = self.make_thumbnail(self.image)
                self.save()
                return self.thumbnail.url
            else:
                return 'https://via.placeholder.com/640x360.jpg'
            

    def make_thumbnail(self, image, size =(300, 300)):
        img = Image.open(image)
        img.convert('RGB')
        img.thumbnail(size)
        thum_io = BytesIO()
        img.save(thum_io, 'JPEG', quality=85)
        thumbnail = File(thum_io, name=image.name)
        return thumbnail
    
## Search feature
class SongQuerySet(models.QuerySet):
    def search(self,query = None):
        if query is None or query == "":
            return self.none() # []
        # lookups = Q(title__icontains = query) | Q(artist__icontains = query) | Q(genre__icontains = query) | Q(album__icontains = query) 
        lookups =( Q(title__icontains = query) |
                   Q(album__title__icontains = query)|
                   Q(genre__name__icontains = query) 
                   )
        return self.filter(lookups) ## this is now reusable
      

class SongManeger(models.Manager):
    def get_queryset(self):
        return SongQuerySet(self.model, using=self._db)

    def search(self, query = None):
        return self.get_queryset().search(query=query)

class Song(models.Model):
    title = models.CharField(max_length=200)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    album = models.ForeignKey(Album,null=True, blank=True, on_delete=models.CASCADE )
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    release_date = models.DateField()
    length = models.PositiveIntegerField(blank=True, null=True, help_text="Length in seconds")
    audio = models.FileField(upload_to=audio_file_path, validators=[FileExtensionValidator(allowed_extensions=['mp3', 'wav', 'ogg'])])
    added_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)

    objects = SongManeger()  # for Search

    @property
    def name(self):
        return self.title   ### name = title 

    def __str__(self):
        return self.title
    

    def get_duration(self):
        if self.length is not None:
            return self.length
    

    def update_duration(self):
        if hasattr(self.audio, 'file') and isinstance(self.audio.file, File):
            try:
                # Read audio file metadata
                audio_info = mutagen.File(self.audio.path).info
                # Set audio duration in seconds
                self.length = int(audio_info.length)
            except Exception as e:
                print(f"Error updating duration: {e}")

    def get_duration(self):
        if self.length is not None:
            minutes, seconds = divmod(self.length, 60)
            return f"{int(minutes)}:{int(seconds):02d}"  # Display as MM:SS format

        return "Unknown"
    

    def get_absolute_url(self):
        return reverse("core:stream_song", kwargs={"song_id": self.id})

    def save(self, *args, **kwargs):
        # Update duration before saving
        self.update_duration()
        super().save(*args, **kwargs)



    def get_play_url(self):
        return reverse("core:play-song", kwargs={"song_id": self.id})
    
    def get_audio_url(self):
        return self.audio.url

    def get_hx_play_url(self):
        return reverse("core:hx-play-song", kwargs={"song_id": self.id})


    


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    songs = models.ManyToManyField('Song', related_name='favorites')
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.songs}"

