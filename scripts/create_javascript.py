#!/usr/bin/env python

if __name__ == "__main__":
    identifiers_json = open("data/identifiers.json").read()
    stations_json = open("data/stations.json").read()

    with open("static/stations.js", "w") as outfile:
        outfile.write(
            f"const stations = {stations_json}; const identifiers = {identifiers_json};"
        )

    print("✨ Written JavaScript to static/stations.js ✨")