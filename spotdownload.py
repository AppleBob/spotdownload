
import os
import sys
from bs4 import BeautifulSoup
import requests
import json
import base64
import yt_dlp
from pydub import AudioSegment

musicType = ""

album = input("paste link to playlist here: ")
if "playlist" in album:
    musicType = "playlists"
if "album" in album:
    musicType = "albums"
try:
    #url = album[album.rfind("/")+1:album.index("?")]
    url = album[:album.index("?")]
except:
    pass

album = url
try:
    while "/" in album:
        album = album[1:]
except:
    pass

stitch = input("Would you like to stitch all the songs together into one file? (Y/N): ")
#CREDENTIALS- DO NOT LEAK
client_id = 
client_secret = 

#encode client_id and client_secret in base64
auth_str = f"{client_id}:{client_secret}"
b64_auth_str = base64.b64encode(auth_str.encode()).decode()

#request token
token_url = "https://accounts.spotify.com/api/token"
headers = {
    "Authorization": f"Basic {b64_auth_str}",
}
data = {
    "grant_type": "client_credentials"
}

response = requests.post(token_url, headers=headers, data=data)
token_info = response.json()
access_token = token_info['access_token']
print("Access token:", access_token)


album_id = album  # example album or playlist id
album_url = f"https://api.spotify.com/v1/{musicType}/{album_id}"


headers = {
    "Authorization": f"Bearer {access_token}"
}

response = requests.get(album_url, headers=headers)
content = response.json()

#save to file
with open("myfile.json", "w", encoding="utf-8") as f:
    json.dump(content, f, indent=4)



songs = {

}



for s in range(len(content["tracks"]["items"])):
    if musicType == "albums":
        songs[content["tracks"]["items"][s]["name"]] = []
        # there could be multiple artists
        for a in range(len(content["tracks"]["items"][s]["artists"])):
            songs[content["tracks"]["items"][s]["name"]].append(content["tracks"]["items"][s]["artists"][a]["name"])
    if musicType == "playlists":
        songs[content["tracks"]["items"][s]["track"]["name"]] = [] #name of song
        # there could be multiple artists
        for a in range(len(content["tracks"]["items"][s]["track"]["artists"])): #corresponding artists
            songs[content["tracks"]["items"][s]["track"]["name"]].append(content["tracks"]["items"][s]["track"]["album"]["artists"][a]["name"])



#print(songs)

ytquerys = []

songtitles = []

for s in songs:
    s1 = str(s)
    s1 = s1.replace(" ", "+")
    s2 = ""
    for x in range(len(songs[s])):
        if x >= 1:
            s2 += "+"
        s2 += str(songs[s][x]).replace(" ", "+")

    s3 = s1+"+by+"+s2

    ytquerys.append("https://www.youtube.com/results?search_query="+s3)
    songtitles.append(s1)

#print(ytquerys)
#quit()

yts = []
#make sure to check for dupe songs, also add a catch for errors where the song already exists in the folder
#find youtube link for each song
for y in ytquerys:
    yt = requests.get(y)
    content = yt.content.decode('utf-8')
    i = content.index('ytInitialData')
    j = content[i:].index('</script>')
    data = json.loads(content[i+16:i+j-1])
    index = 0
    while True:
        video=list(data["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"][index].items())[0][1]
        if not ("ads" in video):
            break
        index = index + 1

    try:
        video = list(data["contents"]["twoColumnSearchResultsRenderer"]
                    ["primaryContents"]["sectionListRenderer"]["contents"][0]
                    ["itemSectionRenderer"]["contents"][index].items())[0][1]

        if "navigationEndpoint" in video and "watchEndpoint" in video["navigationEndpoint"]:
            video_id = video["navigationEndpoint"]["watchEndpoint"]["videoId"]
        elif "videoId" in video:
            video_id = video["videoId"]  #fallback if direct videoId exists
        else:
            print("no videoId found")
            continue

        url = "https://www.youtube.com/watch?v=" + video_id
        yts.append(url)

    except KeyError as e:
        print(f"skipping due to KeyError: {e}")
    except Exception as e:
        print(f"unexpected error: {e}")

    #endpoint = video["navigationEndpoint"]["watchEndpoint"]
    #url="https://www.youtube.com/watch?v=" + endpoint["videoId"]
    #yts.append(url)


track = None

# download and stitch
for y in range(len(yts)):
    title = songtitles[y].replace("+", " ")
    out_file = f"{title}.mp3"

    ydl_opts = {
        'format': 'bestaudio',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f"{title}.%(ext)s",
        'downloader': 'aria2c',
        'downloader_args': {'aria2c': '-x 16 -s 16 -k 1M'},
        'ffmpeg_location': r'C:\FFmpeg\bin',
        'socket_timeout': 60,
        'retries': 10,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([yts[y]])

    # After download, assume final file is .mp3
    filepath = os.path.join(os.getcwd(), out_file)

    if not os.path.isfile(filepath):
        print(f"[Warning] Skipped: {filepath} not found.")
        continue

    song = AudioSegment.from_file(filepath, format="mp3")

    if stitch.lower() == "y":
        if track is None:
            track = song
        else:
            track += song
        os.remove(filepath)

# export final album
if stitch.lower() == "y" and track:
    output_path = os.path.join(os.getcwd(), "album.mp3")
    track.export(output_path, format="mp3")
    print(f"[Done] Stitched album saved to: {output_path}")

print("\n\nDONE! Check the folder this program is in.\n")

"""
    print(y)
    yt = YouTube(y, on_progress_callback=on_progress)
    #Download mp3
    audio_file = yt.streams.filter(only_audio=True).first().download()
    base, ext = os.path.splitext(audio_file)
    new_file = base + '.mp3'
    os.rename(audio_file, new_file)"
"""
    

