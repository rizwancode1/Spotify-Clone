from django.urls import path

from .views import home_view ,profile,songs_search_view ,playlist_view ,playlist_create_view , play_song  ,favorites ,hx_menu_favorites ,manage_favorites ,hx_play_song

app_name = 'core'

urlpatterns = [
    path('', home_view, name='home' ), 
    path('profile/<int:user_id>/', profile , name='profile'),
    path('list/<int:playlist_id>/', playlist_view, name='list-view' ),
    path('playlist/create' ,playlist_create_view, name='create_playlist'),
    path('favorites/', favorites, name='favorites'),
    path('manage-favorites/<int:song_id>/', manage_favorites, name='manage-favorites'),
    path('play_song/<int:song_id>/', play_song, name='play-song'),
    path('search/',songs_search_view , name='search' ),

    path('hx_play_song/<int:song_id>/', hx_play_song, name='hx-play-song'),
    path('hx_favorites/', hx_menu_favorites, name='hx_menu_favorites'),
   
]
