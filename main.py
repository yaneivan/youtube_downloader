from pytube import YouTube
from pytube.cli import on_progress
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
import os
import requests 
import shutil
from pydub import AudioSegment
from uuid import uuid4
import time

'''
00:00 Эпоха для нас
03:50 Я люблю шокировать
08:40 Комсомольский билет
13:39 Анаконда
20:09 Кто не с нами
23:08 МК-ультра
27:54 Юбер-любер
32:14 Энтузиазм
'''

#  https://www.youtube.com/watch?v=dNr7nXvntO8


def download_video(link):
	yt = YouTube(link)
	streams = yt.streams
	best_quality_stream = streams.get_highest_resolution()
	best_quality_stream.download()

def download_thumbnail(link, name):
	name = str(uuid4()) + link[-4:]
	pic = requests.get(link, stream = True)
	if pic.status_code == 200:
		with open(name, 'wb') as f:
			shutil.copyfileobj(pic.raw, f)

	return name

def set_image(yt_link, audio_path):
	yt = YouTube(yt_link)
	title = yt.title
	thumbnail = yt.thumbnail_url
	picture_path = download_thumbnail(thumbnail, title.replace('.mp4', ''))
	audio = MP3(audio_path, ID3=ID3)
	audio.tags.add(APIC(mime='image/jpeg',type=3,desc=u'Cover',data=open(picture_path,'rb').read()))
	audio.save()
	return picture_path


#default show progress from pytube won't work, write your own!
def download_audio(link, show_progress=False):
	if show_progress:
		yt = YouTube(link, on_progress_callback=on_progress)
	else:
		yt = YouTube(link)
	#thumbnail = yt.thumbnail_url
	title = yt.title 
	best_audio_stream = yt.streams.filter(only_audio=True).get_audio_only()
	title = best_audio_stream.download()#os.path.join(os.getcwd(), title+'.mp4'))
	#command_for_converting = 'ffmpeg -y -loglevel quiet -i "'+ title + '" "' + title.replace('mp4', 'mp3')+'"'
	command_for_converting = 'ffmpeg.exe  -i "'+ title + '" "' + title.replace('mp4', 'mp3')+'"'
	if os.name == 'posix':
		command_for_converting = command_for_converting.replace('ffmpeg.exe', 'ffmpeg')
	os.system(command_for_converting)
	os.remove(title)
	audio_path = title.replace('mp4', 'mp3')
	picture_path = set_image(link, audio_path)
	os.remove(picture_path)
	return audio_path

def time_name_split(text):
	text = list(text.split())
	name = ' '.join(text[1:])
	return (text[0], name)


def parse_timestamps(arr_stamps, verbose = 0):
	arr_stamps.remove('')
	print(arr_stamps)
	for index, stamp in enumerate(arr_stamps):
		#arr_stamps[index] = stamp.split()
		arr_stamps[index] = Timestamp(stamp)
		if verbose > 0:
			print('name:', arr_stamps[index].name, end = ' \n')
			print('starts at:', arr_stamps[index].start_time, '\n')
	return arr_stamps

class Timestamp:
	def __init__(self, input_string):
		time, name = time_name_split(input_string)
		if time.count(':') == 1:
			time = list(time.split(':'))
			self.start_time = int(time[0])*60*1000 + int(time[1])*1000
		elif time.cont(':') == 2:
			time = list(time.split(':'))
			self.start_time = int(time[0])*60*60*1000 + int(time[1])*60*1000 + int(time[2])*1000

		self.name = name

	def __str__(self):
		return str(self.start_time) + " " + self.name


if __name__ == "__main__":
	print("""
Welcome to youtube dowbloader by yaneivan!
What would you like to download?
(You can input multiple links, separated by space)
1) Video
2) Song
3) Parse an album""")
	target = input()
	if target == '1':
		link = input('Please enter link to the video: ')
		if ' ' in link:
			links = link.split(' ')
			for link in links:
				download_video(link)
		else:
			download_video(link)

	elif target == '2':
		link = input('Please enter link to the song: ')
		if ' ' in link:
			links = link.split(' ')
			for link in links:
				download_audio(link)
		else:
			download_audio(link)


	elif target == '3':
		link = input('Please enter link to the album: ')
		print("Please input timestamps in a format like:\n11:11 first_song\n22:22 second\n")
		
		inp = ' '
		arr_stamps = []
		while inp != '':
			inp = input()
			arr_stamps.append(inp)

		l_path = download_audio(link, show_progress=True)
		print(l_path)
		AudioSegment.converter = "ffmpeg.exe"
		album = AudioSegment.from_mp3(l_path)
		arr_stamps = parse_timestamps( arr_stamps) # returns list of class Timestamps
		
		songs = []
		for index in range(len(arr_stamps)-1):
			songs.append(album[arr_stamps[index].start_time : arr_stamps[index+1].start_time])
		songs.append(album[arr_stamps[-1].start_time:])

		for index, song in enumerate(songs):
			song.export(arr_stamps[index].name+".mp3", format="mp3")
			time.sleep(3)
			print("Debug", "link", link,"song", song)
			set_image(link, arr_stamps[index].name+".mp3")


print('Done.')
