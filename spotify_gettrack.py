#imports
import base64
import json
import os
import subprocess
import serial
import time
import re
import urllib, urllib2

#constants
PREFIX_SONG = "S"
PREFIX_PLAYING = "P"
PREFIX_META = "M"

API_ENABLED = True
API_CLIENT_ID = "YOUR_CLIENT_ID"
API_CLIENT_SECRET = "YOUR_CLIENT_SECRET"
API_REDIRECT_URI = "YOUR_CALLBACK_URI"


#global vars
s1883 = False
schange = False
playing = 0

curuser = None

#functions
# from http://stackoverflow.com/a/20078869/1896516
def remove_non_ascii(text):
	return ''.join([i if ord(i) < 128 else '\x0E' for i in text])

def spotify_load_refresh_token():
	if os.path.isfile("token.dat"):
		with open("token.dat", "r") as tf:
			token = tf.read()
			spotify_refresh_access_token(token)
			return True

	else: return False


def spotify_save_refresh_token(token):
	with open("token.dat", "w") as tf:
		tf.write(token)

def spotify_refresh_access_token(token):
	global api_access_token
	url = "https://accounts.spotify.com/api/token"
	data = urllib.urlencode({
			'grant_type':'refresh_token',
			'refresh_token':token
		})
	req = urllib2.Request(url, data=data, headers={'Authorization':'Basic ' + base64.b64encode(API_CLIENT_ID + ":" + API_CLIENT_SECRET)})
	try:
		resp = urllib2.urlopen(req)
	except urllib2.HTTPError, err:
		print(err.code)
		print(err.read())
		return
	global api_access_token
	api_access_token = json.load(resp)
	api_access_token['timestamp'] = time.time()
	#only save a new refresh key if we were given one
	if 'refresh_token' in api_access_token.keys():
		spotify_save_refresh_token(api_access_token['refresh_token'])
	else:
		api_access_token['refresh_token'] = token

def spotify_get_access_token(auth):
	url = "https://accounts.spotify.com/api/token"
	data = urllib.urlencode({
			'grant_type':'authorization_code',
			'code':auth,
			'redirect_uri': API_REDIRECT_URI
		})
	req = urllib2.Request(url, data=data, headers={'Authorization':'Basic ' + base64.b64encode(API_CLIENT_ID + ":" + API_CLIENT_SECRET)})
	try:
		resp = urllib2.urlopen(req)
	except urllib2.HTTPError, err:
		print(err.code)
		print(err.read())
		return
	global api_access_token
	api_access_token = json.load(resp)
	api_access_token['timestamp'] = time.time()
	spotify_save_refresh_token(api_access_token['refresh_token'])

def spotify_check_token_expiry():
	if api_access_token['timestamp'] + api_access_token['expires_in'] <= time.time():
		spotify_refresh_access_token(api_access_token['refresh_token'])

def spotify_get_user_id():
	spotify_check_token_expiry()
	req = urllib2.Request("https://api.spotify.com/v1/me", headers={'Accept':'application/json', 'Authorization': 'Bearer '+api_access_token['access_token']})
	return json.load(urllib2.urlopen(req))['id']

def spotify_get_saved(trackid):
	spotify_check_token_expiry()
	req = urllib2.Request("https://api.spotify.com/v1/me/tracks/contains?ids="+trackid, headers={'Accept':'application/json', 'Authorization': 'Bearer '+api_access_token['access_token']})
	return json.load(urllib2.urlopen(req))[0]

def spotify_get_playlists(user, limit, offset):
	spotify_check_token_expiry()
	req = urllib2.Request("https://api.spotify.com/v1/users/" + user + "/playlists?limit=" + str(limit) + "&offset=" + str(offset), headers={'Accept':'application/json', 'Authorization': 'Bearer '+api_access_token['access_token']})
	return json.load(urllib2.urlopen(req))

def spotify_get_liked(trackid):
	global curuser
	spotify_check_token_expiry()
	listid = ""
	offset = 0
	if curuser == None:
		curuser = spotify_get_user_id()
	#for as long as we don't have a playlist id
	while listid == "":
		#get 50 lists at position offset from the current user
		obj = spotify_get_playlists(curuser, 50, offset)
		#check each list for the name to be 'Liked from Radio'
		for list in obj['items']:
			if list['name'] == "Liked from Radio":
				listid = list['id']
				break
		#check if there are no more lists left, if so return false (couldn't find a liked list)
		if obj['total'] - obj['offset'] <= 50:
			return False

	#get all the tracks in the playlist
	req = urllib2.Request("https://api.spotify.com/v1/users/" + curuser + "/playlists/" + listid + "/tracks?fields=items.track.id", headers={'Accept':'application/json', 'Authorization': 'Bearer '+api_access_token['access_token']})
	obj = json.load(urllib2.urlopen(req))
	#go through the track ids and check for ours
	for track in obj['items']:
		if track['track']['id'] == trackid:
			return True

	return False

#begin main program

ser = serial.Serial('/dev/ttyACM0', 9600)

proc = subprocess.Popen(['spotify'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)

if(API_ENABLED):
	if not spotify_load_refresh_token():
		auth = raw_input("Enter your auth token: ")
		spotify_get_access_token(auth)
	global curuser
	curuser = spotify_get_user_id()

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
				outstring = PREFIX_META + "|"
				if spotify_get_saved(trackid):
					outstring += "1|"
				else:
					outstring += "0|"

				if spotify_get_liked(trackid):
					outstring += "1\n"
				else:
					outstring += "0\n"
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
