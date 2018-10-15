import csv
import os
import pprint
import re
import shutil
import tempfile

import fiona
import requests

dir_name = 'boundaries/build/rajya-sabha-constituencies'

if not os.path.exists(dir_name):
    os.makedirs(dir_name)

for ext in ('-COPYRIGHT', '.cpg', '.csv', '.dbf', '.prj', '.qpj', '.shp', '.shx'):
    shutil.copy('boundaries/build/states/states' + ext,
                os.path.join(dir_name, 'rajya-sabha-constituencies' + ext))

q = """\
SELECT ?id ?idLabel ?constituency ?constituencyLabel {
  ?id wdt:P31/wdt:P279* wd:Q131541 .

  FILTER NOT EXISTS { ?id wdt:P576 ?dissolvedDate }
  FILTER NOT EXISTS { ?id wdt:P31 wd:Q4808085 }

  ?constituency wdt:P31 wd:Q57156205 ;
                wdt:P131 ?id .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,hi". }
}"""

r = requests.post('https://query.wikidata.org/sparql', q, headers={
    'Accept': 'application/sparql-results+json',
    'Content-Type': 'application/sparql-query'})
r.raise_for_status()
r = r.json()

m = {rs['id']['value'][31:]: rs['constituency']['value'][31:] for rs in r['results']['bindings']}
pprint.pprint(m)

with open(os.path.join(dir_name, 'rajya-sabha-constituencies.csv')) as f:
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as g:
        reader = csv.DictReader(f)
        writer = csv.DictWriter(g, fieldnames=reader.fieldnames)
        writer.writeheader()
        for row in reader:
            row['WIKIDATA'] = m[row['WIKIDATA']]
            row['MS_FB'] = re.sub('country:in/(state|territory):', 'country:in/rajya-sabha-constituency:', row['MS_FB'])
            writer.writerow(row)
shutil.move(g.name, f.name)

# Rewrite shapefiles with fixed IDs and Wikidata IDs
with fiona.open(os.path.join(dir_name, 'rajya-sabha-constituencies.shp'), 'r') as old_shp:
    meta = old_shp.meta

    with fiona.open(os.path.join(dir_name, 't.shp'), 'w', encoding='utf-8', **meta) as new_shp:
        for feature in old_shp:
            feature['properties']['WIKIDATA'] = m[feature['properties']['WIKIDATA']]
            feature['properties']['MS_FB'] = feature['properties']['MS_FB'].replace('country:in/state:', 'country:in/rajya-sabha-constituency:')
            feature['properties']['MS_FB'] = re.sub('country:in/(state|territory):', 'country:in/rajya-sabha-constituency:', feature['properties']['MS_FB'])
            new_shp.write(feature)

for ext in ('.cpg', '.prj', '.dbf', '.shp', '.shx'):
    shutil.move(os.path.join(dir_name, 't' + ext),
                os.path.join(dir_name, 'rajya-sabha-constituencies' + ext))
