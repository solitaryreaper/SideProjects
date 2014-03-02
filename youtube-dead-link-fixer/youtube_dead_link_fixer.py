#!/usr/bin/python

'''
Created on Oct 16, 2013

@author: excelsior
'''

import urllib2, json

# This is the simple key for accessing non-account specific youtube data
SIMPLE_DEVELOPER_KEY = "AIzaSyB7J0D2jG5kVTRPxjT2yGzH6WOE8SCvrXs"
YOUTUBE_SERVICE_BASE_URL = "https://www.googleapis.com/youtube/v3/"
MAX_RESULTS = 50

def get_playlist_songs(playlist_id):
    """
        Returns all the songs corresponding to a playlist URL
    """
    api_call = YOUTUBE_SERVICE_BASE_URL + "playlistItems?part=snippet"
    api_call = api_call + "&maxResults=" + str(MAX_RESULTS) +"&playlistId=" + playlist_id + "&key=" + SIMPLE_DEVELOPER_KEY
    #print "API Call for songs of a playlist :" + api_call
    
    songs_json = urllib2.urlopen(api_call)
    playlist_songs_obj = parse_json(songs_json)
    print playlist_songs_obj
    
    song_wrappers = playlist_songs_obj['items']
    print "Number of songs in playlist :  " + str(len(song_wrappers))
    for song_wrapper in song_wrappers:
        song_name = song_wrapper['snippet']['title']
        song_id = song_wrapper['snippet']['resourceId']['videoId']
        
        is_song_active = is_song_url_active(song_id)
        print "Title : " + song_name + ", Id : " + song_id + ", Active ? " + str(is_song_active)

def get_my_playlists():
    """
        Returns all the playlist URLs for a user
    """
    pass

def is_song_url_active(song_video_id):
    """
        Determines if the youtube song URL is broken
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

    best_search_result_json = urllib2.urlopen(api_call)
    song_video_obj = parse_json(best_search_result_json)

    content = song_video_obj['items']
    song_video_id = content[0]['id']['videoId']

    return song_video_id

def add_song_to_playlist(song_url, playlist_url):
    """
        Adds a new song to the playlist
    """
    pass

def remove_song_from_playlist(song_url, playlist_url):
    """
        Removes a song from the playlist
    """
    pass

def parse_json(json_string):
    """
        Parses json to return a fully populated object
    """
    parsed_json_object = None
    if json_string is not None:
        parsed_json_object = json.load(json_string)
        
    return parsed_json_object

if __name__ == '__main__':
    # Get songs for my Jan-12 playlist. This has both dead as well as active links
    # get_playlist_songs("PL4C8AA3EAAC856623")
    
    # A test playlist - PLSVmge2Vrmn21gsF-hIfu2ryDCyO7qFf2

    keywords = "best+love+song"
    best_song_id = get_best_song_with_keywords(keywords)
    print "Song Id for keywords " + keywords + " is " + best_song_id


    """
    #Test if songs are valid/broken
    valid_song_id = "PDBCg5qeSqs"
    broken_song_id = "ziGR8ZCVHSA"
    
    print "Is song id " + valid_song_id + " active ? " + str(is_song_active(valid_song_id))
    print "Is song id " + valid_song_id + " active ? " + str(is_song_active(broken_song_id))
    """    
    
    