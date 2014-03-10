# -- coding: utf-8 --
#!/usr/bin/python

'''
Created on Oct 16, 2013

@author: excelsior
'''

import urllib2, json, httplib2, os, json, sys

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run

CLIENT_SECRETS_FILE = "client_secrets.json"

# Helpful message to display if the CLIENT_SECRETS_FILE is missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the APIs Console
https://code.google.com/apis/console#access

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__), CLIENT_SECRETS_FILE))

# An OAuth 2 access scope that allows for full read/write access.
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# This is the simple key for accessing non-account specific youtube data
SIMPLE_DEVELOPER_KEY = "AIzaSyB7J0D2jG5kVTRPxjT2yGzH6WOE8SCvrXs"
YOUTUBE_SERVICE_BASE_URL = "https://www.googleapis.com/youtube/v3/"
MAX_RESULTS = 50

def output(text):
    return text.encode('utf-8').strip()

class PlayListSong(object):
    
    def __init__(self, name, playlist_item_id, video_id):
        self.name = name
        self.playlist_item_id = playlist_item_id
        self.video_id = video_id
        
    def __str__(self):
        return "Song : " + output(self.name) + ", Playlist Item Id : " + output(self.playlist_item_id) + ", Video Id : " + output(self.video_id)
    
def get_playlist_songs(playlist_id):
    """
        Returns all the songs corresponding to a playlist URL
        
        Found an issue where this API call does not fetch broken videos because they have been
        deleted altogether. It is not even possible to fetch song metadata for such cases. These
        songs don't even appear in the list of songs in playlist and hence have to be manually
        weeded out :(
    """
    api_call = YOUTUBE_SERVICE_BASE_URL + "playlistItems?part=snippet"
    api_call = api_call + "&maxResults=" + str(MAX_RESULTS) +"&playlistId=" + playlist_id + "&key=" + SIMPLE_DEVELOPER_KEY
    
    songs_json = urllib2.urlopen(api_call)
    playlist_songs_obj = parse_json(songs_json)
    
    playlist_songs = []
    song_wrappers = playlist_songs_obj['items']
    for song_wrapper in song_wrappers:
        playlist_item_id = song_wrapper['id']
        song_name = song_wrapper['snippet']['title']
        song_id = song_wrapper['snippet']['resourceId']['videoId']

        playlist_songs.append(PlayListSong(song_name, playlist_item_id, song_id))
        
    return playlist_songs

def get_my_playlists():
    """
        Returns all the playlist URLs for a user
    """
    pass

def is_song_url_active(song_video_id):
    """
        Determines if the youtube song URL is broken.
        
        Apparently this fixes only these kind of errors
        (
            This video has been removed because its content violated YouTube's Terms of Service        
        )
    """
    api_call = YOUTUBE_SERVICE_BASE_URL + "videos?part=snippet&id=" + song_video_id + "&key=" + SIMPLE_DEVELOPER_KEY
    print "API Call for validating video song :" + api_call
    
    songs_json = urllib2.urlopen(api_call)
    song_video_obj = parse_json(songs_json)
    
    content = song_video_obj['items']
    if content is None or len(content) == 0:
        return False
    
    return True

def get_best_song_with_keywords(keywords):
    """
        Searches for the best active song based on the keywords
    """
    api_call = YOUTUBE_SERVICE_BASE_URL + "search?part=snippet&maxResults=1&q=" + keywords + "&key=" + SIMPLE_DEVELOPER_KEY
    print "API call for getting best song result is : " + api_call

    song_video_id = None
    try:
        best_search_result_json = urllib2.urlopen(api_call)
        song_video_obj = parse_json(best_search_result_json)
    
        content = song_video_obj['items']
        song_video_id = content[0]['id']['videoId']
    except Exception, err:
        print "Failed to search alternate song for keywords : " + keywords
    
    return song_video_id

def add_song_to_playlist(youtube_obj, song_id, playlist_id):
    """
        Adds a new song to the playlist
    """
    is_song_added_to_playlist = True
    try:
        youtube_obj.playlistItems().insert(
            part = "snippet",
            body = 
            {
            'snippet': {
              'playlistId': playlist_id, 
              'resourceId': {
                  'kind': 'youtube#video',
                  'videoId': song_id
                }
              }
             }    
        ).execute()
    except Exception, err:
        is_song_added_to_playlist = False
        print "Failed to add song " + output(song_id) + " to playlist " + output(playlist_id) + ". Reason : " + str(err)
        
    return is_song_added_to_playlist

def remove_song_from_playlist(youtube_obj, playlist_song_id):
    """
        Removes a song from the playlist
    """
    is_song_deleted_from_playlist = True
    try:
        youtube_obj.playlistItems().delete(id=playlist_song_id).execute()
    except Exception, err:
        is_song_deleted_from_playlist = False
        print "Failed to delete playlist song " + output(playlist_song_id) + ". Reason : " + str(err)
        
    return is_song_deleted_from_playlist

def parse_json(json_string):
    """
        Parses json to return a fully populated object
    """
    parsed_json_object = None
    if json_string is not None:
        parsed_json_object = json.load(json_string)
        
    return parsed_json_object

def get_authenticated_service():
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_READ_WRITE_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)

    storage = Storage("%s-oauth2.json" % sys.argv[0])
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run(flow, storage)

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
        http=credentials.authorize(httplib2.Http()))
    
def get_search_keywords_for_song(song_name):
    tokens = song_name.split(" ")
    search_keywords = []
    for token in tokens:
        token = token.strip()
        token = ''.join(c for c in token if c.isalnum())
        if len(token) < 2:
            continue
        
        search_keywords.append(token)

    search_keywords_string = "+".join(token for token in search_keywords)
    return search_keywords_string
    
if __name__ == '__main__':
    if len(sys.argv) > 2:
        print "Invalid arguments. Syntax : <script> <playlist_id>"
        sys.exit()
        
    youtube_obj = get_authenticated_service()
    playlist_id = sys.argv[1]
    
    print "Listing songs for playlist : " + output(playlist_id)
    playlist_songs = get_playlist_songs(playlist_id)
    
    total_songs = len(playlist_songs)
    songs_fixed = 0
    songs_permanently_lost = 0
    
    fixed_songs = []
    lost_songs = []
    
    for playlist_song in playlist_songs:
        print "\n"
        print str(playlist_song)
        
        is_song_active = is_song_url_active(playlist_song.video_id)
        if is_song_active:
            print "Song " + output(playlist_song.name) + " is active .."
        else:
            print "Song " + output(playlist_song.name) + " is not active .."
            
            print "Deleting inactive song " + playlist_song.video_id + " from current playlist .."
            is_song_deleted = remove_song_from_playlist(youtube_obj, playlist_song.playlist_item_id)
            if is_song_deleted:
                print "Successfully deleted inactive song : " + playlist_song.video_id + " from playlist .."
                
                if playlist_song.name == "Private video" :
                    songs_permanently_lost = songs_permanently_lost + 1
                    lost_songs.append(playlist_song.video_id)
                    print "Song " + playlist_song.video_id + " is a private video !! Sorry this song can't be recovered !!"
                    continue
                
                search_keywords_string = get_search_keywords_for_song(playlist_song.name)
                alt_song_video_id = get_best_song_with_keywords(search_keywords_string)
                print "Adding alternate video for this song : " + output(alt_song_video_id)
                if not alt_song_video_id:
                    print "Failed to find alternate song for " + search_keywords_string
                    continue
                
                is_song_added = add_song_to_playlist(youtube_obj, alt_song_video_id, playlist_id)
                if is_song_added:
                    print "Successfully added new song " + output(alt_song_video_id) + " to current playlist .."
                    songs_fixed = songs_fixed + 1
                    fixed_songs.append(playlist_song.name)
                else:
                    print "Failed to add new song " + output(alt_song_video_id) + " to current playlist .."

    print "\n\n --------------------------- Run summary ---------------------------"
    print "#Total songs : " + str(total_songs)
    print "#Fixed songs : " + str(songs_fixed)
    print "#Lost songs : " + str(songs_permanently_lost)
    print "Fixed songs : " + str(fixed_songs)
    print "Lost songs : " + str(lost_songs)