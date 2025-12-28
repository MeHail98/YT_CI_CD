import requests
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="./.env")
API_KEY = os.getenv("API_KEY")
Channel = 'MrBeast'

def get_playlist_id():
    try:
        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={Channel}&key={API_KEY}"
        r = requests.get(url)
        r.raise_for_status

        channel_items = r.json()['items'][0]
        channel_playlistId = channel_items['contentDetails']['relatedPlaylists']['uploads']
        return channel_playlistId
    except requests.exceptions.RequestException as e:
        raise e
    
if __name__ == "__main__":
    print (get_playlist_id())