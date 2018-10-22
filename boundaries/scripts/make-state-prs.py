import collections
import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap

import fiona
import requests

def git(*args):
    return subprocess.check_call(['git'] + list(args))

def query_wikidata(query):
    response = requests.post('https://query.wikidata.org/sparql',
                             data=query,
                             headers={'Accept': 'application/sparql-results+json',
                                      'Content-Type': 'application/sparql-query'})
    response.raise_for_status()
    return response.json()

def item_uri_to_id(item):
    if isinstance(item, dict):
        assert item['type'] == 'uri'
        item = item['value']
    assert item.startswith('http://www.wikidata.org/entity/')
    return item[len('http://www.wikidata.org/entity/'):]

def fix_india_id(id):
    """
    Fix "MS_FB" and "MS_FB_PARE fields in India
    """
    fixes = {
        'country:in/state:cs': 'country:in/state:ct',
        'country:in/state:ts': 'country:in/state:tg',
        'country:in/state:uk': 'country:in/state:ut',
        'country:in/state:od': 'country:in/state:or',
        'union-territory': 'territory'
    }
    for old, new in fixes.items():
        id = id.replace(old, new)

    return id

try:
    github_access_token = os.environ['GITHUB_ACCESS_TOKEN']
except KeyError:
    raise AssertionError('No GITHUB_ACCESS_TOKEN found in environment; '
                         'set one up at https://github.com/settings/tokens and add it to your environment.')


github_headers = {
    'Authorization': 'Token ' + github_access_token,
    'Content-Type': 'application/json',
    'Accept': 'application/vnd.github.mercy-preview+json',
}
pulls_url = 'https://api.github.com/repos/everypolitician/proto-commons-india/pulls'

response = requests.get(pulls_url) #, headers=github_headers)
response.raise_for_status()
pull_heads = {pull['head']['ref'] for pull in response.json()}

metadata_query = """\
SELECT ?id ?language ?idLabel ?house ?houseLabel ?areaType ?areaTypeLabel ?position ?positionLabel {
  ?id wdt:P31/wdt:P279* wd:Q131541 .

  FILTER NOT EXISTS { ?id wdt:P576 ?dissolvedDate }
  FILTER NOT EXISTS { ?id wdt:P31 wd:Q4808085 }

  OPTIONAL { ?id wdt:P37/wdt:P424 ?language }

  OPTIONAL {
    ?house wdt:P31 wd:Q3091020 ;
           wdt:P1001 ?id .
    OPTIONAL {
      ?areaType p:P279 ?statement .
      ?statement ps:P279 wd:Q11774263 ;
                 pq:P642 ?house .
    }
    OPTIONAL {
      ?house wdt:P527 ?position .
      ?position wdt:P279* wd:Q4175034 .
    }
  }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,hi". }
}
"""
metadata = collections.defaultdict(lambda: {'languages': {'hi'}})
for result in query_wikidata(metadata_query)['results']['bindings']:
    id = item_uri_to_id(result['id'])
    if 'idLabel' in result:
        metadata[id]['label'] = result['idLabel']['value']
    if 'language' in result and result['language']['value'] != 'en':
        metadata[id]['languages'].add(result['language']['value'])
    if 'areaType' in result:
        metadata[id]['area_type'] = item_uri_to_id(result['areaType'])
    if 'position' in result:
        metadata[id]['position'] = item_uri_to_id(result['position'])
        metadata[id]['position_comment'] = result['positionLabel']['value']

states_to_skip = {
    'gujarat-ac',  # Not yet fully reconciled
    'jammu-&-kashmir-ac',  # Not yet fully reconciled
    'madhya-pradesh-ac',  # Not yet fully reconciled
    'karnataka-ac',  # Not yet fully reconciled
    'maharashtra-ac',  # Not yet fully reconciled
    'sikkim-ac',  # Not yet fully reconciled
    'tamil-nadu-ac',  # Not yet fully reconciled
}

state_ids = {
    'andhra-pradesh-ac': 'Q1159',
    'arunachal-pradesh-ac': 'Q1162',
    'assam-ac': 'Q1164',
    'bihar-ac': 'Q1165',
    'chhattisgarh-ac': 	'Q1168',
    'delhi-ac': 'Q1353',
    'goa-ac': 'Q1171',
    'gujarat-ac': 'Q1061',
    'haryana-ac': 'Q1174',
    'himachal-pradesh-ac': 'Q1177',
    'jammu-&-kashmir-ac': 'Q1180',
    'jharkhand-ac': 'Q1184',
    'karnataka-ac': 'Q1185',
    'kerala-ac': 'Q1186',
    'madhya-pradesh-ac': 'Q1188',
    'maharashtra-ac': 'Q1191',
    'manipur-ac': 'Q1193',
    'meghalaya-ac': 'Q1195',
    'mizoram-ac': 'Q1502',
    'nagaland-ac': 'Q1599',
    'orissa-ac': 'Q22048',  # Odisha, odisha-ac
    'puducherry-ac': 'Q66743',
    'punjab-ac': 'Q22424',
    'rajasthan-ac': 'Q1437',
    'sikkim-ac': 'Q1505',
    'tamil-nadu-ac': 'Q1445',
    'telangana-ac': 'Q677037',
    'tripura-ac': 'Q1363',
    'uttarkhand-ac': 'Q1499',
    'uttar-pradesh-ac': 'Q1498',
    'west-bengal-ac': 'Q1356',
}

git('fetch')

for name in sorted(os.listdir('boundaries/build')):
    if not os.path.isdir(os.path.join('boundaries/build', name)) or not name.endswith('-ac'):
        continue
    print("Trying", name)
    if name in states_to_skip:
        sys.stderr.write("Directory {} explicitly excluded; skipping.\n".format(name))
        continue

    reconciled_csv_fn = os.path.join('boundaries', 'build', name, name + '-reconciled.csv')
    try:
        with open(reconciled_csv_fn) as f:
            reader = csv.DictReader(f)
#            if 'toreconcile' in reader.fieldnames:
#                sys.stderr.write("Marked as to be reconciled: {}; skipping.\n".format(reconciled_csv_fn))
#                continue
            if 'WIKIDATA' not in reader.fieldnames:
                sys.stderr.write("No WIKIDATA column in {}; skipping.\n".format(reconciled_csv_fn))
                continue
    except FileNotFoundError:
        sys.stderr.write("Couldn't find {}; skipping.\n".format(reconciled_csv_fn))
        continue

    print("Processing {}".format(name))
    boundary_dir = os.path.join('boundaries/build', name)
    branch_name = 'scripted-{}'.format(name)
    state_metadata = metadata[state_ids[name]]
    ms_fb_to_wikidata = {}

    git('checkout', '--no-track', '-B', branch_name, 'origin/add-states')
    if os.path.exists(os.path.join(boundary_dir, name + '.csv')):
        sys.stderr.write("State {} already on add-states branch ({}); skipping.\n".format(state_metadata['label'], name))
        git('checkout', 'reconciling')
        continue
    git('checkout', 'reconciling', '--',
        *[os.path.join(boundary_dir, name + ext)
          for ext in ('.cpg', '.csv', '.dbf', '.prj', '.shp', '.shx', '-reconciled.csv')])
    git('reset')

    # Add '-ur' to unreconciled files
    for ext in ('.cpg', '.csv', '.dbf', '.prj', '.shp', '.shx'):
        shutil.move(os.path.join(boundary_dir, name + ext),
                    os.path.join(boundary_dir, name + '-ur' + ext))

    # Move '-reconciled.csv' to the standard place
    shutil.move(os.path.join(boundary_dir, name + '-reconciled.csv'),
                os.path.join(boundary_dir, name + '.csv'))

    # Rewrite incorrect MS_FB and MS_FB_PARE ids
    with open(os.path.join(boundary_dir, name + '.csv'), 'r') as f:
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as g:
            reader = csv.DictReader(f)
            writer = csv.DictWriter(g, fieldnames=reader.fieldnames)
            writer.writeheader()
            for row in reader:
                row['MS_FB'] = fix_india_id(row['MS_FB'])
                row['MS_FB_PARE'] = fix_india_id(row['MS_FB_PARE'])
                writer.writerow(row)
                ms_fb_to_wikidata[row['MS_FB']] = row['WIKIDATA']
    shutil.move(g.name, os.path.join(boundary_dir, name + '.csv'))

    # Pick up other labels for items
    query = """
        SELECT ?id ?label WHERE {{
            VALUES ?id {{ {} }}
            ?id rdfs:label ?label
            FILTER(LANG(?label) IN ({}))
        }}
    """.format(
        " ".join("wd:{}".format(id) for id in ms_fb_to_wikidata.values()),
        ", ".join(repr(l) for l in state_metadata['languages']),
    )
    labels = requests.post('https://query.wikidata.org/sparql',
                           data=query,
                           headers={'Accept': 'application/sparql-results+json',
                                    'Content-Type': 'application/sparql-query'}).json()
    item_labels = collections.defaultdict(dict)
    for result in labels['results']['bindings']:
        item_labels[result['id']['value'].rsplit('/', 1)[1]][result['label']['xml:lang']] = result['label']['value']

    lang_mapping = {}
    for language in state_metadata['languages']:
        fieldname = 'NAME_' + language.upper().replace('-', '_')
        lang_mapping[fieldname] = language

    # Put those labels in the CSV
    with open(os.path.join(boundary_dir, name + '.csv'), 'r') as f:
        fieldnames = reader.fieldnames
        for fieldname in sorted(lang_mapping):
            if fieldname not in fieldnames:
                fieldnames.append(fieldname)
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as g:
            reader = csv.DictReader(f)
            writer = csv.DictWriter(g, fieldnames=fieldnames)
            writer.writeheader()
            for row in reader:
                row['MS_FB'] = fix_india_id(row['MS_FB'])
                row['MS_FB_PARE'] = fix_india_id(row['MS_FB_PARE'])
                for fieldname, language in lang_mapping.items():
                    row[fieldname] = item_labels[row['WIKIDATA']].get(language, '')
                writer.writerow(row)
    shutil.move(g.name, os.path.join(boundary_dir, name + '.csv'))

    # Rewrite shapefiles with fixed IDs and Wikidata IDs
    with fiona.open(os.path.join(boundary_dir, name + '-ur.shp'), 'r') as old_shp:
        meta = old_shp.meta
        if 'WIKIDATA' not in meta['schema']['properties']:
            meta['schema']['properties']['WIKIDATA'] = 'str:254'
        for fieldname in sorted(lang_mapping):
            if fieldname not in meta['schema']['properties']:
                meta['schema']['properties'][fieldname] = 'str:254'

        with fiona.open(os.path.join(boundary_dir, name + '.shp'), 'w', encoding='utf-8', **meta) as new_shp:
            for feature in old_shp:
                feature['properties']['MS_FB'] = fix_india_id(feature['properties']['MS_FB'])
                feature['properties']['MS_FB_PARE'] = fix_india_id(feature['properties']['MS_FB_PARE'])
                try:
                    wikidata_id = ms_fb_to_wikidata[feature['properties']['MS_FB']]
                except KeyError:
                    wikidata_id = ''
                    sys.stderr.write("Missing {} from CSV for {}\n".format(feature['properties']['MS_FB'], name))
                feature['properties']['WIKIDATA'] = wikidata_id
                for fieldname, language in lang_mapping.items():
                    feature['properties'][fieldname] = item_labels[wikidata_id].get(language, '')
                new_shp.write(feature)

    # Commit everything
    git('add', os.path.join(boundary_dir, name + '.csv'))
    git('commit', '-m', 'Add CSV for {} assembly constituencies'.format(state_metadata['label']))

    git('add', *[os.path.join(boundary_dir, name + ext)
                 for ext in ('.cpg', '.dbf', '.prj', '.shp', '.shx')])
    git('commit', '-m', 'Add shapefile for {} assembly constituencies'.format(state_metadata['label']))

    license_fn = os.path.join(boundary_dir, name + '-COPYRIGHT')
    with open(license_fn, 'w') as f:
        f.write(textwrap.dedent("""
            The dataset is shared under Creative Commons Attribution 2.5 India license.
            
            https://github.com/datameet/maps/tree/master/assembly-constituencies
        """))
    git('add', license_fn)
    git('commit', license_fn, '-m', 'Add license for {} assembly constituencies'.format(state_metadata['label']))

    # Add metadata entry
    index_fn = 'boundaries/build/index.json'
    with open(index_fn) as f:
        index_data = json.load(f)
    if not any(entry['directory'] == name for entry in index_data):
        index_data.append({
            'directory': name,
            'area_type_wikidata_item_id': state_metadata['area_type'],
            'associations': [{
                'comment': state_metadata['position_comment'],
                'position_item_id': state_metadata['position'],
            }],
            'name_columns': {
                'lang:en': 'AC_NAME',
                **{'lang:' + v: k for k, v in lang_mapping.items()},
            }
        })
        with open(index_fn, 'w') as f:
            json.dump(index_data, f, indent=2)
        git('add', index_fn)
        git('commit', '-m', 'Add metadata for {} assembly constituencies'.format(state_metadata['label']))

    with open('build_output.txt', 'w') as f:
        subprocess.check_call(['bundle', 'exec', 'build', 'build'], stdout=f)
    git('add', 'build_output.txt')
    git('commit', '-a', '-m', 'Rebuild with boundary data for {} assembly constituencies'.format(state_metadata['label']))

    try:
        git('rev-parse', '--verify', branch_name + '@{u}')
    except subprocess.CalledProcessError:  # retcode 128 if no known remote branch
        git('push', '-u', 'origin', branch_name)
    else:  # there's a remote branch, so --force-with-lease to it
        git('push', 'origin', branch_name, '--force-with-lease')

    try:
        git('rev-parse', '--verify', branch_name + '@{u}')
    except subprocess.CalledProcessError:  # retcode 128 if branch doesn't exist
        git('push', '-u', 'origin', branch_name)
    else:  # branch exists, so let's push with --force-with-lease
        git('push', 'origin', branch_name, '--force-with-lease')

    if branch_name in pull_heads:
        sys.stderr.write("Pull request already exists.\n")
    else:
        response = requests.post(
            pulls_url,
            json.dumps({
                'title': 'State: {} [auto-generated]'.format(state_metadata['label']),
                'head': branch_name,
                'base': 'add-states',
                'body': 'Add states data for {}'.format(state_metadata['label']),
            }),
            headers=github_headers,
        )
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            sys.stderr.write("Couldn't create pull request ({}).\n".format(e.response.status_code))
        else:
            sys.stderr.write("Pull request created: {}\n".format(response.json()['html_url']))

    git('checkout', 'reconciling')

