SideProjects
============

A collection of fun side-projects that I did along the way ..

1) COMPANY LANGUAGE STACK GENERATOR
===================================

A simple python script that scrapes github for a company and returns a summary result of the most prominent languages used in that company. It can give a good insight on the tech stack used by a company. I personally believe this is a good feature that GITHUB itself should provide - summary statistics about a github handle like languages used across projects, average test coverage and other such useful summary metrics.
  
    Usage Example : python company_tech_stack_generator.py https://github.com/walmartlabs
    Total github projects (with language info) for https://github.com/walmartlabs : 44
  
Most Used Languages
-------------------

- JavaScript 68.18 % 
- Objective-C 22.73 % 
- Scala 2.27 % 
- C++ 2.27 % 
- Clojure 2.27 % 
- Ruby 2.27 % 


2) YOUTUBE DEAD LINK FIXER
==========================

I just hate it when a song link in my youtube playlist is broken because the underlying video is deleted. Using youtube data API, this can be fixed. To make youtube playlist modifications, you need to call youtube API with apt keys (https://code.google.com/p/youtube-api-samples/source/browse/samples/python/playlist_updates.py). You need to add a client_secrets.json file which will have the secret keys that allows you to access your private content on youtube. Access to public entities can be done with the public key in my script. This script runs as follows :

    python youtube_dead_link_fixer.py <playlist id to be fixed>
    Example : python youtube_dead_link_fixer.py PLAFB78EFDE5A6259A
