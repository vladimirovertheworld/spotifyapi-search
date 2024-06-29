import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import json
import os

# Load credentials from the file
with open('creds_spotify.json', 'r') as file:
    creds = json.load(file)

# Authenticate with Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=creds['client_id'],
                                               client_secret=creds['client_secret'],
                                               redirect_uri=creds['redirect_uri'],
                                               scope="playlist-read-private"))

def search_playlists_by_genre(genres):
    results = []
    for genre in genres:
        playlists = sp.search(q=f'genre:{genre}', type='playlist', limit=50)
        for playlist in playlists['playlists']['items']:
            # Fetch detailed playlist information to get the follower count
            playlist_id = playlist['id']
            detailed_playlist = sp.playlist(playlist_id)
            results.append({
                'name': detailed_playlist['name'],
                'followers': detailed_playlist['followers']['total'],
                'owner': detailed_playlist['owner']['display_name'],
                'link': detailed_playlist['external_urls']['spotify']
            })
    return results

def main():
    genres = ['drum and bass', 'idm', 'electro']
    playlists = search_playlists_by_genre(genres)

    # Convert results to DataFrame and sort by followers
    df = pd.DataFrame(playlists)
    df = df.sort_values(by='followers', ascending=False)

    print(df.to_string(index=False))

if __name__ == '__main__':
    main()
