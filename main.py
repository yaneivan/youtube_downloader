from pytube import YouTube
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
import os
import requests 
import shutil

def download_video(link):
	yt = YouTube(link)
	streams = yt.streams
	best_quality_stream = streams.get_highest_resolution()
	best_quality_stream.download()

def download_thumbnail(link, name):
	name = name+link[-4:]
	pic = requests.get(link, stream = True)
	if pic.status_code == 200:
		with open(name, 'wb') as f:
			shutil.copyfileobj(pic.raw, f)

def download_audio(link):
	yt = YouTube(link)
	thumbnail = yt.thumbnail_url
	title = yt.title 
	best_audio_stream = yt.streams.filter(only_audio=True).get_audio_only()
	title = best_audio_stream.download()#os.path.join(os.getcwd(), title+'.mp4'))
	command_for_converting = 'ffmpeg.exe -y -loglevel quiet -i "'+ title + '" "' + title.replace('mp4', 'mp3')+'"'
	if os.name == 'posix':
		command_for_converting = command_for_converting.replace('ffmpeg.exe', 'ffmpeg')
	os.system(command_for_converting)
	os.remove(title)
	audio_path = title.replace('mp4', 'mp3')
	download_thumbnail(thumbnail, title.replace('.mp4', ''))
	picture_path = title.replace('.mp4', '') + thumbnail[-4:]
	print(picture_path)
	audio = MP3(audio_path, ID3=ID3)
	#audio.add_tags()
	audio.tags.add(APIC(mime='image/jpeg',type=3,desc=u'Cover',data=open(picture_path,'rb').read()))
	audio.save()
	os.remove(picture_path)


print("""Welcome to youtube dowbloader by yaneivan!
What would you like to download?
1) Video
2) Song""")
target = input()
if target == '1':
	link = input('Please enter link to the video: ')
	download_video(link)
elif target == '2':
	link = input('Please enter link to the song: ')
	download_audio(link)
print('Done.')
