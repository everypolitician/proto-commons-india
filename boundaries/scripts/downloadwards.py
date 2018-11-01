#!/usr/bin/env python

import requests
import urllib.request, json

with open('../source/wards/wards_links.txt', 'r') as links:
    for link in links:

        municipality = link.split('/')[-2]
        outfile = '../source/wards/{}-wards.geojson'.format(municipality)
        with urllib.request.urlopen(link) as url:
            data = json.loads(url.read().decode())
            with open(outfile, 'w') as f:
                json.dump(data, f)
