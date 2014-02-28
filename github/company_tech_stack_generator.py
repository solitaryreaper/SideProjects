from bs4 import BeautifulSoup
import urllib2
import sys

'''
Created on Feb 27, 2014

@author: excelsior
'''

"""
    Simple script that scrapes github to generate the most used programming languages by a 
    tech company. This is a rough reflection of the technology stack/ language ecosystem used in
    that company.
"""

def get_language_stats_from_page_html(html):
    language_stats = {}
    soup = BeautifulSoup(html)
    
    projects = soup.findAll('span', {'itemprop' : 'programmingLanguage'})
    for project in projects:
        language = project.text.strip()
        if language in language_stats.keys():
            language_stats[language] = language_stats[language] + 1
        else:
            language_stats[language] = 1
            
    return language_stats

"""
    Collect languages stats from all the github pages for this company
"""
def get_language_stats_by_company(github_base_url):
    page = 0
    overall_language_stats = {}
    
    are_all_pages_done = False
    while not  are_all_pages_done:
        page = page + 1
        url = github_base_url + "?page=" + str(page)
        #print "\nScraping url : " + url
        html = urllib2.urlopen(url).read()
        page_language_stats = get_language_stats_from_page_html(html)
        if not page_language_stats:
            are_all_pages_done = True
            #print "Done scraping all pages for url " + github_base_url
            break
        
        for language, cnt in page_language_stats.iteritems():
            if language in overall_language_stats.keys():
                overall_language_stats[language] = overall_language_stats[language] + cnt
            else:
                overall_language_stats[language] = cnt
        
    return overall_language_stats
    
"""
    Check if the github handle is a valid URL
"""    
def check_if_valid_url(company_url):
    is_valid_url = True
    try:
        html = urllib2.urlopen(company_url).read()
    except Exception:
        is_valid_url = False
        
    return is_valid_url
    
if __name__ == '__main__':
    args = sys.argv[1:2]
    company_url = args[0].strip()
    is_valid = check_if_valid_url(company_url)
    if not is_valid:
        print "URL " + company_url + " is not valid. Please enter the correct github handle !!"
        sys.exit()
        
    stats = get_language_stats_by_company(company_url)
    total_projects = 0
    for key in stats.keys():
        total_projects = total_projects + stats[key]
        
    print "Total github projects (with language info) for " + company_url + " : " + str(total_projects)
    print "\n=========================== MOST USED LANGUAGES ==================================="
    for language in sorted(stats, key=stats.get, reverse=True):
        language_percent = stats[language]/float(total_projects)*100
        print language, str(round(language_percent, 2)) + " % "
