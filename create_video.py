import json
import subprocess
import requests
import uuid
import time
import logging
import random

EN_API_KEY = "Z5BUWFNXJP6NGXADB"
VID_HEMAN = "ZZ5LpwO-An4.flv"
VID_SENTINEL = "V1b7sDq0AkI.mp4"
VID_FLASH = "y9he--ojipI.flv"
VID = VID_HEMAN

def create_vid(mp3_path, youtube_url):
    vid_path = None#get_vid(youtube_url)
    fn = ffmpeg_process(vid_path, mp3_path)
    return fn

def get_vid(youtube_url):
    filename = "/home/echonest/tdb/vids/%s.flv" % str(uuid.uuid4())[:10]
    z = subprocess.Popen("/home/echonest/tdb/youtube-dl/youtube-dl.dev %s > %s" % (youtube_url, filename), shell=True)
    z.wait()
    return filename 

def track_upload_analyze(audio_path):
    base_url = "http://developer.echonest.com/api/v4"
    url = "%s/track/upload?api_key=%s" % (base_url, EN_API_KEY)
    url += "&filetype=mp3&format=json"
    audio = {'track': open(audio_path, 'rb').read()}
    r = requests.post(url, data=audio)
    json_re = json.loads(r.text)
    track_id = json_re['response']['track']['id']
    url = "%s/track/profile/" % base_url
    url += "?api_key=%s&format=json&id=%s&bucket=audio_summary" % (EN_API_KEY, track_id)
    r = requests.get(url)
    json_re2 = json.loads(r.text)
    analysis_url = json_re2['response']['track']['audio_summary']['analysis_url']
    print analysis_url
    r = requests.get(analysis_url)
    print r.__dict__
    print r.content
    ree = json.loads(r.content)
    return (ree['beats'], ree['segments'])

def cut_up_video(vid, index, total_secs, duration):
    print duration
    start = random.randint(50, int(total_secs-duration)-60)
    ffmpeg_call = "./ffmpeg -ss %s -t %s -i %s %s" % (start, duration, VID, "/mnt/tdb/segs/%s.mpg" % index)
    z = subprocess.Popen(ffmpeg_call, shell=True)
    z.wait()

def merge_vids(index):
    cmd = "cat %s | ./ffmpeg -f mpeg -i - -vcodec mpeg4 -an output.mp4"
    files = " ".join(["/mnt/tdb/segs/%s.mpg" % i for i in range(index+1)])
    cmd = cmd % files
    z = subprocess.Popen(cmd, shell=True)
    z.wait()

def ffmpeg_process(vid, audio_path):
    proc = subprocess.Popen('./ffmpeg -i %s 2>&1 | grep "Duration" | cut -d " " -f 4 | sed s/,//' % VID,
                    shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    text_dur = proc.stdout.readline()
    hours, mins, secs = text_dur.split(":")
    total_secs = int(hours.strip())*3600+int(mins.strip())*60+int(secs.strip().split(".")[0])
    #audio_path = "/Users/jsteinbach/Downloads/Baauer-Swerve.mp3"
    #audio_path = "/Users/jsteinbach/Downloads/phantom.mp3"
    #audio_path = "/Users/jsteinbach/Downloads/earthquake.mp3"
    #audio_path = "/Users/jsteinbach/Downloads/paranoid.mp3"
    #audio_path = "/Users/jsteinbach/Downloads/detroit.mp3"
    beats, segs = track_upload_analyze(audio_path)
    numbeats = len(beats)
    for i, beat in enumerate(beats):
        cut_up_video(VID, i, total_secs, beat['duration'])
    merge_vids(i)
    random_name = str(uuid.uuid4())[:10]
    cmd = "./ffmpeg -i output.mp4 -i %s -map 0 -map 1 -codec copy /mnt/tdb/static/output_%s.mp4" % (audio_path, random_name)
    z = subprocess.Popen(cmd, shell=True)
    z.wait()
    return 'output_%s.mp4' % random_name
    

