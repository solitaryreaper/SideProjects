'''
Created on Mar 21, 2014

@author: excelsior
'''

"""
    Given a list of sites, determines which sites are archived on Wayback Machine and for such sites
    returns the latest snapshot URL.
"""

import urllib2, json, sys

WAYBACK_MACHINE_BASE_URL = "http://archive.org/wayback/available?url="

def get_latest_snapshot(url):
    """
        Returns the latest snapshot URL for a site if it is archived. 
        Else returns None.
    """
    if not url:
        return None
    
    api_url_to_invoke = WAYBACK_MACHINE_BASE_URL + url
    results = urllib2.urlopen(api_url_to_invoke)
    results_json_obj = json.load(results)
    
    archived_snapshots = results_json_obj['archived_snapshots']
    if not archived_snapshots:
        return None
    
    return archived_snapshots['closest']['url']

def find_sites_with_archived_content(urls):
    """
        Finds all the sites which have archived content and returns their latest snapshot URL.
    """
    archived_content_map = {}
    for url in urls:
        snapshot_url = get_latest_snapshot(url)
        if snapshot_url:
            archived_content_map[url] = snapshot_url
            
    return archived_content_map

if __name__ == '__main__':
    sites_input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    print "Input file : " + sites_input_file + ", Output file : " + output_file
    
    urls = []
    with open(sites_input_file) as f:
        urls = f.readlines()
        
    archived_content_map = find_sites_with_archived_content(urls)
    
    out = open(output_file, 'w')
    out.write("URL,Latest Snapshot URL")
    for url, snapshot_url in archived_content_map.iteritems():
        print "URL : " + url + " , Snapshot URL : " + snapshot_url
        out_line = url.strip() + "," + snapshot_url.strip() + "\n" 
        out.write(out_line)
    out.close()
