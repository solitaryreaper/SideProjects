import pylast
import urllib2, json, httplib2, os, json, sys, time, re
from bs4 import BeautifulSoup

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

MUSIC_GENRE_CATEGORY = "music genre"
ARTIST_CATEGORY = "artist"
SOUNDTRACK_CATEGORY = "soundtrack"
MUSIC_SINGLE_CATEGORY = "music single"

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
    tags = []
    try:
        track = network.get_track_by_mbid(mbid)
    except Exception, err:
        print "Failed to finf track info for " + str(mbid)
        return tags
    
    lastfm_tags = track.get_top_tags(limit=DEFAULT_NUMBER_TAGS_TO_FETCH)

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

def get_genre_details_from_topic(topic_id):
    url = FREEBASE_SERVICE_URL + topic_id + "?key=" + SIMPLE_DEVELOPER_KEY
    #print "Topic Search URL : " + url
    
    genres = []
    try:
        topic = json.loads(urllib2.urlopen(url).read())
        category = get_topic_category(topic)
        
        # If freebase music category object, easy to find music genres
        if category == MUSIC_GENRE_CATEGORY:
            raw_genres = topic['property']['/type/object/name']['values']
            genres = [genre['text'].strip().lower() for genre in raw_genres if len(genre['text'].strip().lower()) > 2]
            print "Music Genre : " + str(genres)
        elif category == MUSIC_SINGLE_CATEGORY or category == ARTIST_CATEGORY :
            # If freebase soundtrack category, navigate using wikipedia link, to get genres using infobox
            if '/common/topic/description' in topic['property']:
                wiki_link = topic['property']['/common/topic/description']['values'][0]['citation']['uri'].strip()
                genres = get_genres_for_song_from_wiki(wiki_link)
                print "Soundtrack  : " + str(genres)
                
            # If musicbrain id available, fetch the tags from musicbrainz site                  
            elif '/common/topic/topic_equivalent_webpage' in topic['property']:
                musicbrainz_url = topic['property']['/common/topic/topic_equivalent_webpage']['values'][0]['value'] + "/tags"
                genres = get_genres_for_song_from_musicbrainz(musicbrainz_url)
                print "Music Single : " + str(genres)
    except Exception, err:
        print "Failed to get genre for topic : " + topic_id + ". Reason : " + str(err)
        
    return genres

def get_topic_category(topic):
    """
        Checks if this topic belongs to the following categories : Music Genre, Artist or Song
    """
    notable_for_obj = topic['property']['/common/topic/notable_for']
    notable_for = notable_for_obj['values'][0]['id'].lower()
    
    notable_types_obj = topic['property']['/common/topic/notable_types']
    notable_types = notable_types_obj['values'][0]['id'].lower()    
    
    category = None
    if "/music/genre" in notable_for or "/music/genre" in notable_types:
        category = MUSIC_GENRE_CATEGORY
    elif "celebrity" in notable_types or "celebrity" in notable_for:
        category = ARTIST_CATEGORY  
    elif "music" in notable_types or "music" in notable_for:
        category = MUSIC_SINGLE_CATEGORY          
            
    return category
    
def get_genres_for_song_from_wiki(url):
    """
        Get genre of a song from wiki infobox
    """
    genres = []
    html = urllib2.urlopen(url).read()
    soup = BeautifulSoup(html)
    
    infobox = soup.find('table', {'class' : re.compile(r".*infobox.*")})
    rows = infobox.findAll('tr')
    for row in rows:
        key, value = "", ""
        try:
            th = row.find('th', {'scope' : 'row'})
            
            key = th.text.strip()
        except Exception, err:
            continue
        
        if "Genre" in key:
            td = row.find('td')
            links = td.findAll('a')
            # Hack : Really need to learn regex well soon !! Some genre infobox text had special characters ..
            genres = [link.text.strip().lower() for link in links if len(link.text.strip().lower().replace("[", "").replace("]", "")) > 2]
            
            # Sometimes the genres don't have hyperlinks
            #Hack : Really need to learn regex well soon !! Some genre infobox text had newline characters ..
            genre_string = td.text.strip().replace("\n", ",").replace("[1][2][3]", "")
            other_genres = [genre.strip().lower() for genre in genre_string.split(",") if len(genre.strip().lower()) > 2]
            
            genres.extend(other_genres)        
    
    unique_genres = list(set(genres))
    return unique_genres
    
def get_genres_for_song_from_musicbrainz(url):
    """
        Get the tags for a song from musicbrainz
    """
    genres = []
    html = urllib2.urlopen(url).read()
    soup = BeautifulSoup(html)
    
    try:
        tags = soup.find('span', {'class' : 'tags'})
        links = tags.findAll('a')
        genres = [link.text.strip().lower() for link in links]
    except Exception, err:
        print "Failed to parse html for musicbrainz URL : " + musicbrainz_url
    
    return genres
    
def parse_json(json_string):
    """
        Parses json to return a fully populated object
    """
    parsed_json_object = None
    if json_string is not None:
        parsed_json_object = json.load(json_string)
        
    return parsed_json_object

def get_genres_from_song_topics(topics):
    """
        Iterates through all the topics for a youtube song and determines the most apt genres for
        the song. The preference order is as follows :
        
        a) If a topic corresponds directly to a music genre on freebase, return it.
        b) If a) fails, find genres from musicbrainz or wiki link for the song.
        c) If a) and b) both fail, get the genres of the artist in general.
    """
    genres = []
    for topic in topics:
        song_genres = get_genre_details_from_topic(topic)
        if song_genres:
            genres.extend(song_genres)

    return list(set(genres))

def analyze_playlist(youtube_playlist_id):
    """
        Analyzes a youtube playlist and generates statistics about the song genres that I 
        generally listen to.
    """
    videos = get_playlist_songs(youtube_playlist_id)
    print "Found " + str(len(videos)) + " songs in the playlist : " + youtube_playlist_id
    
    genre_stats = {}
    songs_wo_genres = []
    
    total_songs = len(videos)
    tagged_songs = 0
    for video_id in videos:
        print "\n\n"
        time.sleep(3)
        
        topics_for_song = get_youtube_song_details(video_id)
        if topics_for_song is None:
            print "Found no topics for song : " + video_id
            continue
        
        print "Topics for song : " + video_id + " are " + str(topics_for_song)
        song_genres = get_genres_from_song_topics(topics_for_song)
        if not song_genres:
            songs_wo_genres.append(video_id)
            print "Found no music genre for song " + str(video_id)
        else:
            tagged_songs = tagged_songs + 1
            for genre in song_genres:
                genre_cnt = 1
                if genre in genre_stats.keys():
                    genre_cnt = genre_cnt + genre_stats.get(genre)

                genre_stats[genre] = genre_cnt            
        
    print "Genre stats : "
    print "------------------------"
    for genre, count in genre_stats.iteritems():
        print genre + "," + str(count)
        
    print "\n#Total songs : " + str(total_songs) + ", #Tagged songs : " + str(tagged_songs)
    print "\nSongs without genre : " + str(songs_wo_genres)
        
def test():
    """
    genres = get_genres_from_wiki("http://en.wikipedia.org/wiki/index.html?curid=30960173")
    print str(genres)
    """
    #get_genre_details_from_topic("/m/0nl_s1y")
    
    #tags = get_tags_for_a_song_by_mbid("61bf0388-b8a9-48f4-81d1-7eb02706dfb0")    
    #tags = get_tags_for_a_song_by_mbid("574eafc0-6909-4278-94fa-083ea5aefc61")
    #tags = get_tags_for_a_song_by_artist_and_song("Cher", "Believe")
    #print str(tags)
    
    #genres = get_genres_for_song_from_musicbrainz("http://musicbrainz.org/recording/574eafc0-6909-4278-94fa-083ea5aefc61/tags")
    #print str(genres)
    
    genres= get_genre_details_from_topic("/m/0134pk")
    print str(genres)
    
    #genres = get_genres_for_song_from_wiki("http://en.wikipedia.org/wiki/Wish_You_Were_Here_(Pink_Floyd_album)")
    #genres = get_genres_for_song_from_wiki("http://en.wikipedia.org/wiki/index.html?curid=12245980")
    #genres = get_genres_for_song_from_wiki("http://en.wikipedia.org/wiki/Set_Fire_to_the_Rain")
    #print str(genres)
        
if __name__ == '__main__':
    analyze_playlist("PLBC9DCE48EF03B283")
    #test()