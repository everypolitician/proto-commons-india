#!/usr/bin/env python3

import csv
import fiona

from pathlib import Path


ac_shp = Path('../build/assembly-constituencies/assembly-constituencies-1.shp')

with fiona.open(str(ac_shp), 'r') as source:
    meta = source.meta

    for f in source:
        state = f['properties']['ST_NAME'].strip().lower().replace(' ', '-')
        state_dir = Path('../build', '{}-ac'.format(state))
        state_shp = state_dir / Path('{}-ac.shp'.format(state))
        state_csv = state_dir / Path('{}-ac.csv'.format(state))
        fieldnames = f['properties'].keys()

        try:
            with fiona.open(str(state_shp), 'a', **meta) as dest:
                dest.write(f)
            with open(str(state_csv), 'a', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writerow(f['properties'])

        except IOError:
            state_dir.mkdir()
            with fiona.open(str(state_shp), 'w', **meta) as dest:
                dest.write(f)
            with open(str(state_csv), 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow(f['properties'])
