#! /usr/bin/env python3

from __future__ import unicode_literals
import youtube_dl
import sys, os
import socketio

CURR_DIR = os.getcwd()

ydl_video_opts = {
    'format': 'mp4/bestvideo',
    'outtmpl': './downloads/%(title)s.%(ext)s',
}

ydl_audio_opts = {
    'format': 'bestaudio/best',
    'outtmpl': './downloads/%(title)s.%(ext)s',
    'postprocessors': [
        {'key': 'FFmpegExtractAudio','preferredcodec': 'mp3',
            'preferredquality': '192',
        },
        {'key': 'FFmpegMetadata'},
    ],
}

sio = socketio.Client()
sio.connect('http://localhost:8888')

def send_link_info(data):
    sio.emit('output', '#'*30)
    sio.emit('output', 'Link received: ' + data['link'])
    sio.emit('output', 'Output format will be: ' + data['format'])

def download_as_video(link):
    sio.emit('output', 'Video download is started...')
    with youtube_dl.YoutubeDL(ydl_video_opts) as ydl:
        try:
            info_dict = ydl.extract_info(link, download=True)
            filename  = info_dict['title'] + '.' + info_dict['ext']
            sio.emit('output', 'Video is downloaded.')
            sio.emit('file-info', filename)
        except:
            sio.emit('output', 'There was a problem about the download. Try it again.')

def download_as_audio(link):
    with youtube_dl.YoutubeDL(ydl_audio_opts) as ydl:
        try:
            info_dict = ydl.extract_info(link, download=True)
            filename  = info_dict['title'] + '.'
            if info_dict['ext'] != "mp3":
                filename += "mp3"
            else:
                filename += info_dict['ext']
            print(filename, 'is downloaded!')
            sio.emit('output', 'Audio is downloaded.')
            sio.emit('file-info', filename)
        except:
            sio.emit('output', 'There was a problem about the download. Try it again.')

@sio.on('connect')
def connect():
    print("I'm connected!")

@sio.on('disconnect')
def disconnect():
    print("I'm disconnected!")

@sio.on('link')
def on_link(data):
    print('I received a link!', data)
    send_link_info(data)
    sio.emit('output', 'Running the downloader script...')
    if (data['format'] == 'Video'):
        download_as_video(data['link'])
    elif (data['format'] == 'Audio'):
        download_as_audio(data['link'])

@sio.on('delete-files')
def on_delete_files(files):
    print("Deleting downloaded files.")
    for filename in files:
        if os.path.exists(os.path.join(CURR_DIR, 'downloads', filename)):
            os.remove(os.path.join(CURR_DIR, 'downloads', filename))

sio.wait()