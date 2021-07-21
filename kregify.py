#!/usr/bin/env python3

from __future__ import unicode_literals
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from requests import get
from youtube_dl import YoutubeDL
from youtubesearchpython import VideosSearch
import youtube_dl
import shutil
import glob
import os
import music_tag
import requests

directory = 'DIRECTORY_HERE'

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="CLIENT_ID",client_secret="CLIENT_SECRET"))

youtubeOptions = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

playlist_id = 'spotify:user:niknocturnal:playlist:4m2FtiQKqtkzLIVOGtZPDY'
results = sp.playlist(playlist_id)
results = results.get('tracks').get('items')
for item in results:
	songName = item.get('track').get('name').replace('/','_').replace('\\','_')
	artistName = item.get('track').get('artists')[0].get('name').replace('/','_').replace('\\','_')	
	albumName = item.get('track').get('album').get('name').replace('/','_').replace('\\','_')
	artworkURL = item.get('track').get('album').get('images')[0].get('url')
	videosSearch = VideosSearch(songName + ' ' + artistName, limit = 1)
	link = (videosSearch.result().get('result')[0].get('link'))
	artistFolder = os.path.join(directory, artistName)
	albumFolder = os.path.join(artistFolder, albumName)

	if not (os.path.isdir(artistFolder)):
		os.mkdir(artistFolder)
	if not (os.path.isdir(albumFolder)):
		os.mkdir(albumFolder.upper())

	with youtube_dl.YoutubeDL(youtubeOptions) as ydl:
		ydl.download([link])
		song = glob.glob(directory + '*.mp3')
		for track in song:
			artworkPath = ''
			music = music_tag.load_file(track)
			artworkDownload = artworkURL.split('/')[-1]
			downloader = requests.get(artworkURL, stream = True)
			downloader.raw.decode_content = True
			with open(artworkDownload, 'wb') as artwork:
				shutil.copyfileobj(downloader.raw, artwork)
				artwork.close()

			allFiles = os.listdir(directory)
			for files in allFiles:
				if ('.' not in files and os.path.isfile(files)):
					artworkPath = directory + files + '.jpg'
					os.rename(directory + files, artworkPath)
					break

			with open(artworkPath, 'rb') as image:
				music['artwork'] = image.read()
				image.close()
								
			music['title'] = songName
			music['tracktitle'] = songName
			music['artist'] = artistName
			music['albumartist'] = artistName
			music['album'] = albumName
			music['compilation'] = False
			music.save()
			del music
			renamed = albumFolder + '/' + artistName + ' - ' + songName + '.mp3'
			os.rename(track, renamed)
			os.remove(artworkPath)
			if (os.path.isfile(directory + '.cache')):
				os.remove(directory + '.cache')

directories = glob.glob(directory+'/*/')

try:
	for folder in directories:
		if ('Kregify' not in folder and os.path.isdir(folder)):
			shutil.move(folder, 'DIRECTORY_HERE')
except:
	pass		
