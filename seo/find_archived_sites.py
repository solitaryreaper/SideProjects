'''
Created on Mar 21, 2014

@author: excelsior
'''

"""
    Given a list of sites, determines which sites are archived on Wayback Machine and for such sites
    returns the latest snapshot URL.
"""

import urllib2, json, sys, time
from bs4 import BeautifulSoup

WAYBACK_MACHINE_BASE_URL = "http://archive.org/wayback/available?url="
ALL_SNAPSHOTS_BASE_URL = "http://wayback.archive.org/web/*/"

def get_latest_snapshot(url):
    """
        Returns the latest snapshot URL for a site if it is archived. 
        Else returns None.
    """
    if not url:
        return None
    
    latest_snapshot = None
    try:
        api_url_to_invoke = WAYBACK_MACHINE_BASE_URL + url
        results = urllib2.urlopen(api_url_to_invoke)
        results_json_obj = json.load(results)
        
        archived_snapshots = results_json_obj['archived_snapshots']
        if archived_snapshots:
            latest_snapshot = archived_snapshots['closest']['url']
    except Exception, err:
        print "Failed to find closest snapshot for URL " + url + ", Reason : " + str(err)
        
    return latest_snapshot

def get_all_snapshots(url):
    """
        Gets all the snapshot urls for this parent site
    """
    all_snapshots = None
    try:
        url_to_invoke = ALL_SNAPSHOTS_BASE_URL + url
        html = urllib2.urlopen(url_to_invoke).read()
        soup = BeautifulSoup(html)
        
        # Fetch the total snapshots, start and end years
        metaDivParaTags = soup.find("div", {"id": "wbMeta"}).findAll('p')
        start_snapshot_year, end_snapshot_year = None, None 
        for para in metaDivParaTags:
            if "Saved" in para.text.strip():
                links = para.findAll('a', href=True)
                
                start_snapshot_obj = links[0].text.strip()
                temp = start_snapshot_obj.split(",")
                start_snapshot_year = int(temp[1].strip())
                
                if len(links) > 1:
                    end_snapshot_obj = links[1].text.strip()
                    temp = end_snapshot_obj.split(",")
                    end_snapshot_year = int(temp[1].strip())
                else:
                    end_snapshot_year = start_snapshot_year            
    
        curr_year = start_snapshot_year
        all_snapshots = []
        while curr_year <= end_snapshot_year:
            year_url = get_archive_yearly_url(url, curr_year)
            year_snapshots = get_yearly_snapshots_for_url(year_url)
            if year_snapshots:
                all_snapshots.extend(year_snapshots)
                
            curr_year = curr_year + 1
                
        print "Found " + str(len(all_snapshots)) + " snapshots for base URL : " + url + " between " + str(start_snapshot_year) + " - " + str(end_snapshot_year)
        
    except Exception, err:
        print "Failed to get all snapshots for URL " + url + ". Reason : " + str(err)    
              
    return all_snapshots

def get_archive_yearly_url(url, curr_year):
    """
        Generates the appropriate yearly wayback machine URL
    """
    return "http://wayback.archive.org/web/" + str(curr_year) + "1230000000*/" + url
    
def get_yearly_snapshots_for_url(url):
    """
        Find all the snapshots on this archive page
    """
    html = urllib2.urlopen(url).read()
    soup = BeautifulSoup(html)
    
    snapshot_divs = soup.findAll("div", {"class" : "date tooltip"})
    snapshot_urls = []
    for snapshot in snapshot_divs:
        data = snapshot.find('div', {"class" : "day"}).find('a')
        snapshot_url = "http://wayback.archive.org" + data['href']
        snapshot_urls.append(snapshot_url)
    
    return snapshot_urls
    
def find_sites_with_archived_content(urls):
    """
        Finds all the sites which have archived content and returns their latest snapshot URL.
    """
    archived_content_map = {}
    for url in urls:
        time.sleep(2)
        print "Analyzing url : " + url
        snapshot_url = get_latest_snapshot(url)
        if snapshot_url:
            all_snapshots_by_url = get_all_snapshots(url)
            archived_content_map[url] = all_snapshots_by_url
            
    return archived_content_map

def test(url):
    return get_all_snapshots(url)

if __name__ == '__main__':
    sites_input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    print "Input file : " + sites_input_file + ", Output file : " + output_file
    
    urls = []
    try:
        with open(sites_input_file) as f:
            urls = f.readlines()
    except Exception, err:
        print "Failed to read URLs from file .. " + str(err)
        sys.exit(1)
        
    archived_content_map = find_sites_with_archived_content(urls)
    print "Found " + str(len(archived_content_map)) + " archived URLS out of total " + str(len(urls)) + " URLS .. \n"
    
    out = open(output_file, 'w')
    out.write("URL, Snapshots, Snapshot URLs\n")
    for url, snapshot_urls in archived_content_map.iteritems():
        print "URL : " + url + " , # Snapshot URL : " + str(len(snapshot_urls))
        out_line = url.strip() + "," + str(len(snapshot_urls)) + "," + "#".join(snapshot_urls) + "\n"
        out.write(out_line)
    out.close()
    
