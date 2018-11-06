#!/bin/bash

mkdir -p ../build/cities

ogr2ogr \
    -sql @make-cities.sql \
    -dialect sqlite \
    -t_srs EPSG:4326 \
    ../build/cities/cities-ur.shp \
    ../source/wards/wards.vrt \
    -lco ENCODING=UTF-8

ogr2ogr \
    -f "CSV" \
    ../build/cities/cities-ur.csv \
    ../build/cities/cities-ur.shp
