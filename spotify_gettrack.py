'''
 ' This file is part of Spotduino.
 '
 ' Spotduino is free software: you can redistribute it and/or modify
 ' it under the terms of the GNU General Public License as published by
 ' the Free Software Foundation, either version 3 of the License, or
 ' (at your option) any later version.
 '
 ' Spotduino is distributed in the hope that it will be useful,
 ' but WITHOUT ANY WARRANTY; without even the implied warranty of
 ' MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 ' GNU General Public License for more details.
 '
 ' You should have received a copy of the GNU General Public License
 ' along with Spotduino.  If not, see <http://www.gnu.org/licenses/>.
'''

#imports
import base64
import hashlib
import json
import os
import subprocess
import serial
import time
import re
import urllib, urllib2

##constants
PREFIX_SONG = "S"
PREFIX_META = "M"
PREFIX_COLOR = "C"
PREFIX_TIME = "T"

ARDUINO_SERIAL_PORT = '/dev/ttyACM0'

#Spotify API settings. Set API_ENABLED to False if you don't want to login to the APIs to load song save/liked state.
#Otherwise, create an app on the Spotify Developer website and input your credentials here. You will also need an
#auth key. See README.md for more info
API_ENABLED = True
API_CLIENT_ID = "YOUR_CLIENT_ID"
API_CLIENT_SECRET = "YOUR_CLIENT_SECRET"
API_REDIRECT_URI = "YOUR_CALLBACK_URI"

##global vars
curuser = None
lastsong = ""
likedradioid = ""

##functions

#This function removes non-ascii characters and replaces them with one that the display can represent
#(from http://stackoverflow.com/a/20078869/1896516)
def remove_non_ascii(text):
	return ''.join([i if ord(i) < 128 else '\x0E' for i in text])

#read the refresh token from the data file
def spotify_load_refresh_token():
	if os.path.isfile("token.dat"):
		with open("token.dat", "r") as tf:
			token = tf.read()
			spotify_refresh_access_token(token)
			return True

	else: return False


#save the refresh token to the data file
def spotify_save_refresh_token(token):
	with open("token.dat", "w") as tf:
		tf.write(token)

#use the refresh token to get a new access token
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

#get the access token from an auth token (first time setup only)
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

#check if the token has expired, if so refresh it
def spotify_check_token_expiry():
	if api_access_token['timestamp'] + api_access_token['expires_in'] <= time.time():
		spotify_refresh_access_token(api_access_token['refresh_token'])

#get the current user's id
def spotify_get_user_id():
	spotify_check_token_expiry()
	req = urllib2.Request("https://api.spotify.com/v1/me", headers={'Accept':'application/json', 'Authorization': 'Bearer '+api_access_token['access_token']})
	return json.load(urllib2.urlopen(req))['id']

#check if the track with id `trackid` is in the user's library
def spotify_get_saved(trackid):
	spotify_check_token_expiry()
	req = urllib2.Request("https://api.spotify.com/v1/me/tracks/contains?ids="+trackid, headers={'Accept':'application/json', 'Authorization': 'Bearer '+api_access_token['access_token']})
	return json.load(urllib2.urlopen(req))[0]

#load the playlists for a user
def spotify_get_playlists(user, limit, offset):
	spotify_check_token_expiry()
	req = urllib2.Request("https://api.spotify.com/v1/users/" + user + "/playlists?limit=" + str(limit) + "&offset=" + str(offset), headers={'Accept':'application/json', 'Authorization': 'Bearer '+api_access_token['access_token']})
	return json.load(urllib2.urlopen(req))

#check if the track with id `trackid` is in the user's "Liked from Radio" playlist
def spotify_get_liked(trackid):
	global curuser, likedradioid
	spotify_check_token_expiry()
	offset = 0
	if curuser == None:
		curuser = spotify_get_user_id()
	#for as long as we don't have a playlist id
	while likedradioid == "":
		#get 50 lists at position offset from the current user
		obj = spotify_get_playlists(curuser, 50, offset)
		#check each list for the name to be 'Liked from Radio'
		for list in obj['items']:
			if list['name'] == "Liked from Radio":
				likedradioid = list['id']
				break
		#check if there are no more lists left, if so return false (couldn't find a liked list)
		if obj['total'] - obj['offset'] <= 50:
			return False

	#get all the tracks in the playlist
	req = urllib2.Request("https://api.spotify.com/v1/users/" + curuser + "/playlists/" + likedradioid + "/tracks?fields=items.track.id", headers={'Accept':'application/json', 'Authorization': 'Bearer '+api_access_token['access_token']})
	obj = json.load(urllib2.urlopen(req))
	#go through the track ids and check for ours
	for track in obj['items']:
		if track['track']['id'] == trackid:
			return True

	return False

#send time to the arduino
def send_time():
	outstring = time.strftime(PREFIX_TIME + "|%H|%M|%S\n", time.localtime())
	ser.write(outstring)
	print("Sent '" + outstring + "' to Arduino!\n")

##begin main program

#open arduino serial port
ser = serial.Serial(ARDUINO_SERIAL_PORT, 9600)

#open spotify, piping stderr to stdout, and stdout to the subproccess pipe so we can read it
#(this is dirty, but it is the only way that seemed to work as expected)
proc = subprocess.Popen(['spotify'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)

#if the api is enabled, load the refresh token. if that fails, prompt for the user's auth token and get access token. either way, load the current user afterwords
if(API_ENABLED):
	if not spotify_load_refresh_token():
		auth = raw_input("Enter your auth token: ")
		spotify_get_access_token(auth)
	global curuser
	curuser = spotify_get_user_id()

#run this forever (well, until we close the program at least)
while True:
	#read a line from the stdout of spotify
	line = proc.stdout.readline()

	#if the line wasn't empty, parse it
	if line != '':
		#check if there's a track id in here
		if "track=spotify:track:" in line: 

			#extract the trackid from the line
			before, after = line.split("track=spotify:track:");
			trackid, end = after.split(",", 1);

			print("trackid: " + trackid + "\n");

			#check if this is the same song as before. if so, ignore it because we don't need to update anything
			if trackid == lastsong: continue
			lastsong = trackid

			#load the track information from the spotify api
			spurl="https://api.spotify.com/v1/tracks/" + trackid
			data = json.load(urllib2.urlopen(spurl))

			print("name: " + data["name"] + "\nartist(s): ")

			#format the artist information
			artstring = ""
			for artist in data["artists"]:
				artstring += artist["name"] + ", "
				print(artist["name"] + ",")

			print("\n")
			artstring = artstring[:-2]

			#create, clean, and send our final song string
			outstring = PREFIX_SONG + "|" + data["name"] + "|" + artstring + "|" + data["album"]["name"] + "\n"
			outstring = remove_non_ascii(outstring)
			ser.write(outstring)
			print("Sent '" + outstring + "' to Arduino!\n")

			#get saved/liked state if API_ENABLED
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

			#set display color to the hash of the trackid (experimental)
			h = hashlib.md5(trackid).hexdigest()

			#wheel code adapted from the Wheel function in the Adafruit NeoPixel library
			#(https://github.com/adafruit/Adafruit_NeoPixel/blob/master/examples/strandtest/strandtest.ino)
			wp = int(h[:2], 16)
			if wp < 85 :
				r = 255-wp*3
				g = 0
				b = wp*3
			elif wp < 170:
				wp -= 85;
				r = 0
				g = wp*3
				b = 255-wp*3
			else:
				wp -= 170;
				r = wp*3
				g = 255-wp*3
				b = 0

			#format and send color data
			outstring = PREFIX_COLOR + "|" + str(r) + "|" + str(g) + "|" + str(b) + "\n"
			ser.write(outstring)
			print("Sent '" + outstring + "' to Arduino!\n")

			send_time()