import random
from django.shortcuts import render ,get_object_or_404 ,redirect
from django.http import StreamingHttpResponse
from django.views.decorators.http import require_GET
from.models import Song , Playlist  , Favorite
from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.decorators import login_required
from django.db.models import Q


# Create your views here.

@login_required
def profile(request, user_id):
    # Use get_object_or_404 to get the user or return a 404 page if not found
    user = get_object_or_404(User, id=user_id)

    favorites = Favorite.objects.filter(user =request.user).count()
    print('favorites', favorites)


    # You can access user profile details through user.socialaccount_set
    # For example, if using Google as a social account provider:
    # google_account = user.socialaccount_set.filter(provider='google').first()
    social_account = SocialAccount.objects.filter(user=user).first()
    profile_pic = social_account.extra_data.get('picture') if social_account else None

    ctx = {
        'user':user,
        'favorites_count':favorites,
        'profile_pic':profile_pic,
    }

    return render(request, 'profile.html', ctx)



def home_view(request):
    playlists = Playlist.objects.all()
    ctx = {
        'playlists':playlists
    }
    return render(request, 'core/home.html', ctx)

def songs_search_view(request):
    query = request.GET.get('q')
    qs = Song.objects.search(query= query)
    print(qs)

    favs = get_object_or_404(Favorite, user= request.user)
    favs_songs = favs.songs.all()
    
    context = {
        'favs_songs': favs_songs,
        "object_list" : qs 
    }
    return render(request, "core/search.html", context=context)

@login_required
def playlist_view(request ,playlist_id):
    playlist = get_object_or_404(Playlist, id= playlist_id)
    songs = playlist.songs.all()
    # User favorites..
    favs = get_object_or_404(Favorite, user= request.user)
    favs_songs = favs.songs.all()
    ctx = {
        'playlist': playlist,
        'songs': songs,
        'favs_songs': favs_songs,
    }
    return render(request, 'core/playlist.html', ctx)

def playlist_create_view(request):
    if request.method == 'POST':
        user = request.user
        playlists_count = Playlist.objects.filter(user=user).count()
        playlist_name = f'Playlist#{playlists_count + 1}'
        playlist = Playlist.objects.create(name=playlist_name, user=user)
        # Redirect to the newly created playlist's detail page
        return redirect('core:list-view', playlist_id=playlist.id)
        # Replace 'playlist_detail' with the name of your playlist detail URL name

    # Handle the case where the user accesses the page via GET (e.g., clicking the button)
    return redirect('core:home')
    

@login_required
def favorites(request):
    favs = get_object_or_404(Favorite, user= request.user)
    songs = favs.songs.all()
    ctx = {
       'songs':songs
    }
    return render(request, 'core/favorites.html', ctx)



@login_required
def play_song(request, song_id):
    song = get_object_or_404(Song, id=song_id)
    ctx ={
        'song':song
    }
    return render(request, 'core/player.html', ctx)


@login_required
def hx_play_song(request, song_id):
    song = get_object_or_404(Song, id=song_id)
    ctx ={
        'song':song
    }

    response = render(request, 'core/partials/hx_player.html', ctx)
    response['HX-Trigger'] = 'update-music-player'
    return response



def hx_menu_favorites(request):
    favs = get_object_or_404(Favorite, user= request.user)
    total = favs.songs.all().count()
    ctx = {
     'total':total,
    }

    return render(request, 'core/partials/menu_favorites.html',ctx)


@login_required
def manage_favorites(request, song_id=None):
    song = get_object_or_404(Song, id=song_id)

    try:
        # Check if the user has already liked the song
        favorites = Favorite.objects.get(user=request.user)
        if song in favorites.songs.all():
            # If the song is already in favorites, remove it
            favorites.songs.remove(song)
        else:
            # If the song is not in favorites, add it
            favorites.songs.add(song)
    except Favorite.DoesNotExist:
        # If the Favorite object doesn't exist, create it and add the song
        fav_s = Favorite.objects.create(user=request.user)
        fav_s.songs.add(song)

    # Get the total number of liked songs
    liked_songs = get_object_or_404(Favorite, user=request.user)
    total = liked_songs.songs.count()

    # Pass the liked songs count to the template
    ctx = {
        'total': total
    }

    response = render(request, 'core/partials/menu_favorites.html', ctx)
    response['HX-Trigger'] = 'update-favs'
    return response



# def play_song(request, song_id):
#     song = get_object_or_404(Song, id=song_id)
#     ctx ={
#         'song':song
#     }
#     return render(request, 'core/player.html', ctx)


## For live song play
# @require_GET
# def stream_song(request, song_id):
#     # Get the song object
#     song = get_object_or_404(Song, id=song_id)

#     def generate_audio_chunks():
#         with open(song.audio.path, 'rb') as file:
#             chunk_size = 8192  # You can adjust the size based on your needs
#             while True:
#                 chunk = file.read(chunk_size)
#                 if not chunk:
#                     break
#                 yield chunk

#     response = StreamingHttpResponse(generate_audio_chunks(), content_type="audio/mp3")
#     return response


