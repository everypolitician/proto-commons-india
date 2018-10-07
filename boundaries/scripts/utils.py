import requests
import csv
import fiona
from copy import deepcopy


WIKIDATA_PATH = "https://www.wikidata.org/wiki/Special:EntityData/"


def item_labels(item_id, langs):
    '''Takes a "Q" id and list of lang codes.
        returns a dict of labels for id'''
    wikidata_json = requests.get(WIKIDATA_PATH + item_id).json()
    wiki_labels = wikidata_json["entities"][item_id]["labels"]
    labels = {}
    for lang in langs:
        if lang in wiki_labels:
            labels[lang] = wiki_labels[lang]["value"]
    return labels


def item_claim_target(item_id, claim_id, qualifier_id=''):
    wikidata_json = requests.get(WIKIDATA_PATH + item_id).json()
    claims = wikidata_json["entities"][item_id]["claims"]
    try:
        if qualifier_id:
            qualifiers = claims[claim_id][0]['qualifiers']
            try:
                return qualifiers[qualifier_id][0]["datavalue"]["value"]["id"]
            except KeyError as e:
                print('no {} claim for {}'.format(claim_id, item_id))
                raise e
        else:
            return claims[claim_id][0]['mainsnak']['datavalue']['value']['id']
    except KeyError:
        print('no {} claim for {}'.format(claim_id, item_id))
        raise e


def get_official_language_code(item_id):
    located_in_id = item_claim_target(item_id, 'P131')
    official_language_id = item_claim_target(located_in_id, 'P37')
    lang_json = requests.get(WIKIDATA_PATH + official_language_id).json()
    claims = lang_json['entities'][official_language_id]['claims']
    return claims['P424'][0]['mainsnak']['datavalue']['value']


def get_names(src_csv, dst_csv, lang, qid_field='WIKIDATA'):
    rows = []
    with open(src_csv, 'r', newline='') as csv_in:
        reader = csv.DictReader(csv_in)
        for row in reader:
            rows.append(row)

    fieldnames = list(rows[0].keys())
    fieldnames.append('NAME_{}'.format(lang.upper()))

    if qid_field not in fieldnames:
        print('{} field not in CSV'.format(qid_field))

    with open(dst_csv, 'w', newline='') as csv_out:
        writer = csv.DictWriter(csv_out, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            if row[qid_field]:
                try:
                    new_name = item_labels(row[qid_field], [lang])[lang]
                    row['NAME_{}'.format(lang.upper())] = new_name
                except KeyError:
                    print('No {} name found for {}'.format(lang, row[qid_field]))
                    row['NAME_{}'.format(lang.upper())] = ''
                writer.writerow(row)
            else:
                print('no {} value in {}'.format(qid_field, row))


def join_csv_attributes_to_shp(csv_path, shp_src_path, shp_out_path,
                               join_fields=['WIKIDATA'], key_field='MS_FB'):
    attribs = {}
    with open(csv_path, 'r', newline='') as csv_in:
        reader = csv.DictReader(csv_in)
        for row in reader:
            attribs[row[key_field]] = row

    with fiona.open(shp_src_path, 'r') as src:
        schema = deepcopy(src.schema)
        for field in join_fields:
            schema['properties'].update({field: 'str:100'})
        with fiona.open(shp_out_path, 'w', schema=schema, crs=src.crs,
                        driver=src.driver, encoding='UTF-8') as dst:
            for feature in src:
                # print(feature['properties'])
                for field in join_fields:
                    try:
                        key = feature['properties'][key_field]
                        value = attribs[key][field]
                        feature['properties'].update({field: value})
                        if not value:
                            print('Value for field {} is missing in {}'.format(
                                field, csv_path))
                    except KeyError:
                        print('{} value: "{}" not found in {}. '.format(
                              key_field, key, csv_path),
                              '{} left blank'.format(field))
                        feature['properties'].update({field: ''})
                dst.write(feature)
