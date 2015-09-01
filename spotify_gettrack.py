#imports
import json
import urllib2, urllib
import subprocess
import serial
import re

#constants
PREFIX_SONG = "S"
PREFIX_PLAYING = "P"
PREFIX_META = "M"

API_ENABLED = True
API_CLIENT_ID = "YOUR_CLIENT_ID"
API_CLIENT_SECRET = "YOUR_CLIENT_SECRET"
API_REDIRECT_URI = "YOUR_CALLBACK_URI"
API_AUTH_TOKEN = "YOUR_AUTH_TOKEN"

#global vars
s1883 = False
schange = False
playing = 0

#functions
# from http://stackoverflow.com/a/20078869/1896516
def remove_non_ascii(text):
	return ''.join([i if ord(i) < 128 else '\x0E' for i in text])

def spotify_refresh_access_token():
	global api_access_token
	url = "https://accounts.spotify.com/api/token"
	data = urllib.urlencode({
			'grant_type':'refresh_token',
			'refresh_token':api_access_token['refresh_token'],
			'client_id':API_CLIENT_ID,
			'client_secret':API_CLIENT_SECRET
		})
	api_access_token = json.load(urllib2.urlopen(url=url, data=data))

def spotify_get_access_token():
	url = "https://accounts.spotify.com/api/token"
	data = urllib.urlencode({
			'grant_type':'authorization_code',
			'code':API_AUTH_TOKEN,
			'redirect_uri': API_REDIRECT_URI,
			'client_id':API_CLIENT_ID,
			'client_secret':API_CLIENT_SECRET
		})
	try:
		resp = urllib2.urlopen(url=url, data=data)
	except urllib2.HTTPError, err:
		print(err.code)
		print(err.read())
		return
	global api_access_token
	api_access_token = json.load(resp)

def spotify_get_saved(trackid):
	req = urllib2.Request("https://api.spotify.com/v1/me/tracks/contains?ids="+trackid, headers={'Accept':'application/json', 'Authorization': 'Bearer '+api_access_token['access_token']})
	return json.load(urllib2.urlopen(req))[0]

#begin main program

ser = serial.Serial('/dev/ttyACM0', 9600)

proc = subprocess.Popen(['spotify'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)

if(API_ENABLED):
	spotify_get_access_token()

while True:
	line = proc.stdout.readline()

	if line != '':
		#check if there's a track id in here
		if "track=spotify:track:" in line: 
			schange = True

			before, after = line.split("track=spotify:track:");
			trackid, end = after.split(",", 1);

			print("trackid: " + trackid + "\n");

			spurl="https://api.spotify.com/v1/tracks/" + trackid
			data = json.load(urllib2.urlopen(spurl))

			print("name: " + data["name"] + "\nartist(s): ")

			artstring = ""

			for artist in data["artists"]:
				artstring += artist["name"] + ", "
				print(artist["name"] + ",")

			print("\n")

			artstring = artstring[:-2]
			outstring = PREFIX_SONG + "|" + data["name"] + "|" + artstring + "|" + data["album"]["name"] + "\n"
			outstring = remove_non_ascii(outstring)
			ser.write(outstring)
			print("Sent '" + outstring + "' to Arduino!\n")

			if(API_ENABLED):
				if(spotify_get_saved(trackid)):
					outstring = PREFIX_META + "|1\n"
				else:
					outstring = PREFIX_META + "|0\n"
				ser.write(outstring)
				print("Sent '" + outstring + "' to Arduino!\n")

		elif "spirc_manager.cpp:1883" in line:
			s1883 = True;

		elif "spirc_manager.cpp:668" in line:
			if s1883:
				if playing: schange = False
				playing = 1
				s1883 = False
			else:
				if not schange:
					playing = 0

				schange = False

			print("Playing: ")
			print(playing)
			print("\n")

			outstring = PREFIX_PLAYING + "|" + str(playing) + "\n"
			ser.write(outstring)
			print("Sent '" + outstring + "' to Arduino!\n")
