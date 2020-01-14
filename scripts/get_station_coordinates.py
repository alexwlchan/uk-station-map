#!/usr/bin/env python
"""
Get a JSON file recording all the stations in the UK and Ireland, and
their lat/long coordinates.

Based on data from:

*   Trainline EU (Great Britain):
    https://github.com/trainline-eu/stations

*   Wikipedia (Ireland/Northern Ireland):
    https://en.wikipedia.org/wiki/List_of_railway_stations_in_Ireland

"""

import csv
import gzip
import io
import json
import re
from urllib.request import urlretrieve

import bs4


def get_trainline_csv_rows():
    """
    Generate every row in the Trainline EU database.
    """
    filename, _ = urlretrieve(
        "https://raw.githubusercontent.com/trainline-eu/stations/master/stations.csv"
    )

    with open(filename) as infile:
        reader = csv.DictReader(infile, delimiter=";")

        for row in reader:
            yield row


def get_wikipedia_rows():
    filename, _ = urlretrieve(
        "https://en.wikipedia.org/wiki/List_of_railway_stations_in_Ireland"
    )

    with open(filename) as infile:
        soup = bs4.BeautifulSoup(infile.read(), "html.parser")

        table = soup.find("table", attrs={"class": "wikitable"})

        rows = iter(table.find_all("tr"))

        field_names = [th_tag.text.strip() for th_tag in next(rows).find_all("th")]

        for row in rows:
            yield dict(
                zip(field_names, [td_tag.text.strip() for td_tag in row.find_all("td")])
            )


if __name__ == "__main__":
    from pprint import pprint

    stations = {}

    for row in get_trainline_csv_rows():

        # The Trainline database includes stations from a lot of countries,
        # but we're only interested in stations in Great Britain.
        #
        # (The Trainline database doesn't seem to include Northern Ireland stations.)
        if row["country"] != "GB":
            continue

        stations[row["name"]] = [row["longitude"], row["latitude"]];

    for row in get_wikipedia_rows():
        if row["Location"] != "Northern Ireland":
            continue

        names = [row["Irish name"], row["English Name"]]
        names = [nm.strip() for nm in names if nm.strip()]

        # The coordinate string is in the format:
        #
        #   1°2′3″N 1°2′3″W\ufeff / \ufeff1.234°N 1.2.3.4°W\ufeff / 1.234; -1.234
        #
        # so we can split on slashes to get the decimal values.
        long_lat_coords = row["Coordinates"].split("/")[-1].strip()
        match = re.match(
            r"^(?P<longitude>-?\d+\.\d+); (?P<latitude>-?\d+\.\d+)$", long_lat_coords
        )
        assert match is not None, long_lat_coords

        stations["/".join(names)] = [match.group("longitude"), match.group("latitude")]

    json_string = json.dumps(stations, separators=(',',':'), sort_keys=True)
    js_string = f"const stations = {json_string};"

    with open("static/stations.js", "w") as out_file:
        out_file.write(js_string)

    print("✨ Written station coordinates to stations.js ✨")
