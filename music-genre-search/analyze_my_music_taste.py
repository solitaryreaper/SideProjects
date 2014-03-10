import pylast
import urllib2, json, httplib2, os, json, sys

# LASTFM constants
# You have to have your own unique two values for LASTFM_API_KEY and API_SECRET
# Obtain yours from http://www.last.fm/api/account for Last.fm
LASTFM_API_KEY = "a64ca166070edab69dd19cd8e1b3c712" # this is a sample key
LASTFM_API_SECRET = "535a2d4b82929b949b2ac3e439e3cb78"

# In order to perform a write operation you need to authenticate yourself
LASTFM_USERNAME = "invinc4u"
LASTFM_PASSWORD_HASH = pylast.md5("Invinc4u71#")

network = pylast.LastFMNetwork(api_key = LASTFM_API_KEY, api_secret = 
    LASTFM_API_SECRET, username = LASTFM_USERNAME, password_hash = LASTFM_PASSWORD_HASH)

DEFAULT_NUMBER_TAGS_TO_FETCH = 3

# Youtube Constants
SIMPLE_DEVELOPER_KEY = "AIzaSyB7J0D2jG5kVTRPxjT2yGzH6WOE8SCvrXs"
YOUTUBE_SERVICE_BASE_URL = "https://www.googleapis.com/youtube/v3/"
MAX_RESULTS = 50

# Freebase constants
FREEBASE_SERVICE_URL = "https://www.googleapis.com/freebase/v1/topic"

def get_tags_for_a_song_by_artist_and_song(artist, title):
    """
        Returns all the tags for a song
    """
    track = network.get_track(artist, title)
    if track is None:
        print "Failed to find track for artist " + artist + ", song " + song
        return None
    else:
        print str(track)
    lastfm_tags = track.get_top_tags(limit=DEFAULT_NUMBER_TAGS_TO_FETCH)
    tags = []
    for tag in lastfm_tags:
        tags.append(tag.item.get_name())
        
    return tags

def get_tags_for_a_song_by_mbid(mbid):
    """
        Returns all the tags for a song identified by a musicbrainz id
    """
    track = network.get_track_by_mbid(mbid)
    if track is None:
        print "Failed to find track for mbid " + mbid
        return None
    else:
        print "hello world .."
        print str(track)
    lastfm_tags = track.get_top_tags(limit=DEFAULT_NUMBER_TAGS_TO_FETCH)
    tags = []
    for tag in lastfm_tags:
        tags.append(tag.item.get_name())
        
    return tags

def get_playlist_songs(playlist_id):
    """
        Returns all the songs corresponding to a playlist URL
    """
    api_call = YOUTUBE_SERVICE_BASE_URL + "playlistItems?part=snippet"
    api_call = api_call + "&maxResults=" + str(MAX_RESULTS) +"&playlistId=" + playlist_id + "&key=" + SIMPLE_DEVELOPER_KEY
    
    songs_json = urllib2.urlopen(api_call)
    playlist_songs_obj = parse_json(songs_json)
    
    videos = []
    song_wrappers = playlist_songs_obj['items']
    for song_wrapper in song_wrappers:
        video_id = song_wrapper['snippet']['resourceId']['videoId']
        videos.append(video_id)
       
    return videos

def get_youtube_song_details(song_video_id):
    """
        Get the list of topics for a song ..
    """
    api_call = YOUTUBE_SERVICE_BASE_URL + "videos?part=topicDetails&id=" + song_video_id + "&key=" + SIMPLE_DEVELOPER_KEY
    print "API Call for validating video song :" + api_call
    
    topics = None
    
    try:
        songs_json = urllib2.urlopen(api_call)
        song_video_obj = parse_json(songs_json)
        
        topics = song_video_obj['items'][0]['topicDetails']['topicIds']
    except Exception, err:
        print "Failed to find topics for song " + song_video_id
    
    return topics

def get_freebase_topic_details(topic_id):
    url = FREEBASE_SERVICE_URL + topic_id + "?filter=suggest&key=" + SIMPLE_DEVELOPER_KEY
    print "Topic Search URL : " + url
    
    genres = None
    try:
        topic = json.loads(urllib2.urlopen(url).read())
        is_music_genre = False
        notable_topic_type_obj = topic['property']['/common/topic/notable_for']
        notable_topic_type = notable_topic_type_obj['values'][0]['text']
        if "musical genre" in str(notable_topic_type).lower():
            print "Yes. Music genre !!"
            is_music_genre = True
        else:
            print "No music genre !!"
            
        if is_music_genre:
            raw_genres = topic['property']['/type/object/name']['values']
            genres = [genre['text'] for genre in raw_genres]
            print str(genres)
    except Exception, err:
        print "Failed to get genre for topic : " + topic_id
    
    for property in topic['property']:
      print property + ':'
      for value in topic['property'][property]['values']:
        print ' - ' + value['text']

        
    return genres
    """
    for property in topic['property']:
      print property + ':'
      for value in topic['property'][property]['values']:
        print ' - ' + value['text']
    """    

def parse_json(json_string):
    """
        Parses json to return a fully populated object
    """
    parsed_json_object = None
    if json_string is not None:
        parsed_json_object = json.load(json_string)
        
    return parsed_json_object

if __name__ == '__main__':
    #get_freebase_topic_details("/m/064t9")
#     tags = get_tags_for_a_song_by_mbid("d1e0a99e-1894-457b-ba6a-985eeef4d0c4")
#     print str(tags)
    
    tags = get_tags_for_a_song_by_artist_and_song("Pharrell Williams", "Happy")
    print str(tags)
    
    """
    youtube_playlist_id = "PLSVmge2Vrmn0sUdJzuOwD0gyn60UneQ6D"
    videos = get_playlist_songs(youtube_playlist_id)
    print "Found " + str(len(videos)) + " songs in the playlist : " + youtube_playlist_id
    genre_stats = {}
    for video_id in videos:
        topics_for_song = get_youtube_song_details(video_id)
        if topics_for_song is None:
            print "Found no topics for song : " + video_id
            continue
        
        print "Topics for song : " + video_id + " are " + str(topics_for_song)
        
        for topic in topics_for_song:
            song_genres = get_freebase_topic_details(topic)
            if song_genres is None:
                print "Found no music genre for topic " + topic + " in freebase API."
                continue
            
            for genre in song_genres:
                genre_cnt = 1
                if genre in genre_stats.keys():
                    genre_cnt = genre_cnt + genre_stats.get(genre)

                genre_stats[genre] = genre_cnt
                
    print "Genre stats : " + str(genre_stats)
    """