#!/usr/bin/env python
"""
Get a map of UK stations you've visited.

You need to register with https://www.transportapi.com/ to make the API calls
to look up station data.

Usage:
  get_uk_station_map.py <STATIONS_TXT> --app_id=<APP_ID> --app_key=<APP_KEY>
  get_uk_station_map.py (-h | --help)

Options:
  -h --help             Show this screen.
  --app_id=<APP_ID>     App ID for transportapi.com
  --app_key=<APP_KEY>   App key for transportapi.com.

"""

import json
import pathlib
import sys
import webbrowser

import docopt
import httpx
import inquirer
import jinja2


def lookup_station(query, *, app_id, app_key):
    try:
        cache = json.load(open("_cache.json"))
    except FileNotFoundError:
        cache = {}

    try:
        return cache[query]
    except KeyError:
        pass

    resp = httpx.get(
        "https://transportapi.com/v3/uk/places.json",
        params={
            "query": query,
            "type": "train_station",
            "app_id": app_id,
            "app_key": app_key
        }
    )

    members = resp.json()["member"]

    if len(members) == 1:
        selected = members[0]
    elif len(members) > 1:
        choices = {
            f"{m['name']} ({m['station_code']})": m
            for m in members
        }

        questions = [
            inquirer.List(
                'selected',
                message=f"What station is {query!r}?",
                choices=sorted(choices.keys())
            ),
        ]

        answers = inquirer.prompt(questions)
        selected = choices[answers["selected"]]
    else:
        sys.exit("Unable to find a station matching {query!r}")

    cache[query] = selected
    with open("_cache.json", "w") as outfile:
        outfile.write(json.dumps(cache, indent=2, sort_keys=True))

    return selected


def render_map(stations):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("."))
    template = env.get_template("map.html")

    return template.render(stations=stations)

    print(template)


if __name__ == "__main__":
    args = docopt.docopt(__doc__)

    app_id = args["--app_id"]
    app_key = args["--app_key"]

    stations = []

    for line in open(args["<STATIONS_TXT>"]):
        # Skip empty lines and comments
        if line.startswith("#") or not line.strip():
            continue

        query = line.strip()

        if not query:
            continue

        stations.append((query, lookup_station(query, app_id=app_id, app_key=app_key)))

    rendered_html = render_map(stations)

    with open("index.html", "w") as outfile:
        outfile.write(rendered_html)

    path = pathlib.Path("index.html").resolve()
    webbrowser.open(f"file://{path}")
