#!/usr/bin/env python
"""
To create the permalinks, we need a persistent set of IDs to identify stations.

These have to be the same, even when we add new stations.
"""

import json


if __name__ == "__main__":
    identifiers = json.load(open("data/identifiers.json"))
    stations = json.load(open("data/stations.json"))

    for station_name in stations:
        if station_name in identifiers.keys():
            continue
        ident = len(identifiers) + 1
        assert ident not in identifiers.values()
        identifiers[station_name] = ident

    json_string = json.dumps(identifiers)
    with open("data/identifiers.json", "w") as outfile:
        outfile.write(json_string)

    print("✨ Assigned identifiers in data/identifiers.json ✨")