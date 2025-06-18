
import os
import sys
from pytube import YouTube
from pytube.cli import on_progress
from bs4 import BeautifulSoup
import requests
import json
import base64
import yt_dlp

"""
client_id = '7d2fc3185542431bbc5b8f52d15aebcb'
client_secret = 'e8f17bd9347345819c61f1e35dda3865'

#encode client credentials
credentials = f"{client_id}:{client_secret}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()

#request access token
token_url = "https://accounts.spotify.com/api/token"
headers = {
    "Authorization": f"Basic {encoded_credentials}",
    "Content-Type": "application/x-www-form-urlencoded"
}
data = {"grant_type": "client_credentials"}

response = requests.post(token_url, headers=headers, data=data)
response_data = response.json()
access_token = response_data.get("access_token")

if access_token:
    print(f"access Token: {access_token}")
else:
    print("failed to obtain access token")
"""



type = ""

album = input("paste link to playlist here: ")
try:
    url = album[:album.index("?")]
except:
    pass
album = url
try:
    while "/" in album:
        album = album[1:]
except:
    pass

html=requests.get(url)
text=html.content.decode('utf-8')
i=text.index('"accessToken"')
j=text.index('"accessTokenExpiration')
token=text[i+15:j-2]
print(token)
#token = access_token
if "album" in url:
    album_url='https://api.spotify.com/v1/albums/' + album
    type = "album"
if "playlist"  in url:
    album_url='https://api.spotify.com/v1/playlists/' + album
    type = "playlist"

response=requests.get(album_url, headers={"authorization":"Bearer " + token})
content=json.loads(response.content.decode('utf-8'))

out_file = open("myfile.json", "w")
json.dump(content, out_file, indent = 6)
  
out_file.close()



songs = {

}





for s in range(len(content["tracks"]["items"])):
    if type == "album":
        songs[content["tracks"]["items"][s]["name"]] = []
        # there could be multiple artists
        for a in range(len(content["tracks"]["items"][s]["artists"])):
            songs[content["tracks"]["items"][s]["name"]].append(content["tracks"]["items"][s]["artists"][a]["name"])
    if type == "playlist":
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


#print(yts)

#download each song
for y in range(0, len(yts)):
    #change outtmpl for name change
    ydl_opts = {
        'format': 'bestaudio',
        'outtmpl': 'audio.%(ext)s',
        'downloader': 'aria2c',
        'downloader_args': {'aria2c': '-x 16 -s 16 -k 1M'},
        'outtmpl': songtitles[y].replace("+", " ")+'.%(ext)s'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([yts[y]])

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
    

