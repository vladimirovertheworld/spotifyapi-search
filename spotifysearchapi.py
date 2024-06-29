import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd

# Replace these with your Spotify API credentials
CLIENT_ID = 'your_client_id'
CLIENT_SECRET = 'your_client_secret'
REDIRECT_URI = 'http://localhost:8888/callback'

# Authenticate with Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope="playlist-read-private"))

def search_playlists_by_genre(genres):
    results = []
    for genre in genres:
        playlists = sp.search(q=f'genre:{genre}', type='playlist', limit=50)
        for playlist in playlists['playlists']['items']:
            results.append({
                'name': playlist['name'],
                'followers': playlist['followers']['total'],
                'owner': playlist['owner']['display_name'],
                'link': playlist['external_urls']['spotify']
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
