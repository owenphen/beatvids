#!/usr/bin/env/python
import requests
import json
import random
import subprocess
EN_API_KEY = "Z5BUWFNXJP6NGXADB"
VID_HEMAN = "ZZ5LpwO-An4.flv"
VID_SENTINEL = "V1b7sDq0AkI.mp4"
VID_FLASH = "y9he--ojipI.flv"

VID = VID_FLASH

def track_upload_analyze(audio_path):
	base_url = "http://developer.echonest.com/api/v4"
	url = "%s/track/upload?api_key=%s" % (base_url, EN_API_KEY)
	url += "&filetype=mp3"
	audio = {'track': open(audio_path,'rb').read()}
	r = requests.post(url, data=audio)
	track_id = r.json['response']['track']['id']
	url = "%s/track/profile/" % base_url
	url += "?api_key=%s&format=json&id=%s&bucket=audio_summary" % (EN_API_KEY, track_id)
	r = requests.get(url)
	analysis_url = r.json['response']['track']['audio_summary']['analysis_url']
	r = requests.get(analysis_url)
	return (r.json['beats'], r.json['segments'])

def cut_up_video(index, total_secs, duration):
	print duration
	start = random.randint(50, int(total_secs-duration)-60)
	ffmpeg_call = "ffmpeg -sameq -ss %s -t %s -i %s %s" % (start, duration, VID, "segs/%s.mpg" % index)
	z = subprocess.Popen(ffmpeg_call, shell=True)
	z.wait()

def merge_vids(index):
	cmd = "cat %s | ffmpeg -f mpeg -i - -sameq -vcodec mpeg4 -an output.mp4"
	files = " ".join(["segs/%s.mpg" % i for i in range(index+1)])
	print files
	cmd = cmd % files
	z = subprocess.Popen(cmd, shell=True)
	z.wait()

if __name__ == "__main__":
	proc = subprocess.Popen('ffmpeg -i %s 2>&1 | grep "Duration" | cut -d " " -f 4 | sed s/,//' % VID,
					shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
	text_dur = proc.stdout.readline()
	hours, mins, secs = text_dur.split(":")
	total_secs = int(hours.strip())*3600+int(mins.strip())*60+int(secs.strip().split(".")[0])
	#audio_path = "/Users/jsteinbach/Downloads/Baauer-Swerve.mp3"
	#audio_path = "/Users/jsteinbach/Downloads/phantom.mp3"
	#audio_path = "/Users/jsteinbach/Downloads/earthquake.mp3"
	#audio_path = "/Users/jsteinbach/Downloads/paranoid.mp3"
	audio_path = "/Users/jsteinbach/Downloads/detroit.mp3"
	beats, segs = track_upload_analyze(audio_path)
	# DO SOMETHING WITH THE SEGMENTS
	numbeats = len(beats)
	for i, beat in enumerate(beats):
		cut_up_video(i, total_secs, beat['duration'])
	merge_vids(i)
	cmd = "ffmpeg -i output.mp4 -i %s -map 0 -map 1 -codec copy output_5.mp4" % audio_path
	z = subprocess.Popen(cmd, shell=True)
	z.wait()
	print "DONE BITCHES! - %s" % numbeats
