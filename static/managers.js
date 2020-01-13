L.TileLayer.Grayscale = L.TileLayer.extend({
	options: {
		quotaRed: 21,
		quotaGreen: 71,
		quotaBlue: 8,
		quotaDividerTune: 0,
		quotaDivider: function() {
			return this.quotaRed + this.quotaGreen + this.quotaBlue + this.quotaDividerTune;
		}
	},

	initialize: function (url, options) {
		options = options || {}
    options.crossOrigin = true;
		L.TileLayer.prototype.initialize.call(this, url, options);

		this.on('tileload', function(e) {
			this._makeGrayscale(e.tile);
		});
	},

	_createTile: function () {
		var tile = L.TileLayer.prototype._createTile.call(this);
    tile.crossOrigin = "Anonymous";
		return tile;
	},

	_makeGrayscale: function (img) {
		if (img.getAttribute('data-grayscaled'))
			return;

    img.crossOrigin = '';
		var canvas = document.createElement("canvas");
		canvas.width = img.width;
		canvas.height = img.height;
		var ctx = canvas.getContext("2d");
		ctx.drawImage(img, 0, 0);

		var imgd = ctx.getImageData(0, 0, canvas.width, canvas.height);
		var pix = imgd.data;
		for (var i = 0, n = pix.length; i < n; i += 4) {
                        pix[i] = pix[i + 1] = pix[i + 2] = (this.options.quotaRed * pix[i] + this.options.quotaGreen * pix[i + 1] + this.options.quotaBlue * pix[i + 2]) / this.options.quotaDivider();
		}
		ctx.putImageData(imgd, 0, 0);
		img.setAttribute('data-grayscaled', true);
		img.src = canvas.toDataURL();
	}
});

class MapManager {
  constructor(div_id) {
    this.map = L.map(div_id);
    this.addOpenstreetMapTiles();

    this.markerCache = {};
  }

  addOpenstreetMapTiles() {
    this.map.setView([54.505, -4.5], 6);

    new L.TileLayer.Grayscale('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, station data from <a href="https://github.com/trainline-eu/stations">Trainline EU</a> and <a href="https://en.wikipedia.org/wiki/List_of_railway_stations_in_Ireland">Wikipedia</a>',
    }).addTo(this.map);
  }

  addMarker(label, long, lat) {
    const marker = L.circle([lat, long], {
      fill: true,
      color: '#0b9e00',
      fillColor: 'rgba(11, 158, 0, 0.3)',
      radius: 7500,
    }).addTo(this.map);

    this.markerCache[label] = marker;
  }

  removeMarker(label) {
    this.map.removeLayer(this.markerCache[label]);
    delete this.markerCache[label];
  }
}

class PickerManager {
  constructor(pickerId, mapManager, stations) {
    this.element = document.getElementById(pickerId);

    this.createChoices();
    this.setupEventListeners(mapManager, stations);
  }

  createChoices() {
    const choices = [];
    for (var name in stations) {
      var data = stations[name];
      choices.push({value: name, label: name});
    }

    const picker = new Choices(this.element, {
      removeItemButton: true,
      choices: choices,
    });

    // Pick a random selection of stations to illustrate the principle.
    // Choose an integer between 3 and 7, then add those stations.
    const randomCount = Math.floor((Math.random() * 5) + 3);

    const items = [];
    for (var i = 0; i < randomCount; i++) {
      var chosenStation = choices[Math.floor(Math.random() * choices.length)];

      var stationName = chosenStation.label;
      var stationCoords = stations[stationName];
      var longitude = stationCoords[0];
      var latitude = stationCoords[1];
      mapManager.addMarker(stationName, longitude, latitude);

      items.push(chosenStation.value);
    }

    picker.setValue(items);
  }

  setupEventListeners(mapManager, stations) {
    this.element.addEventListener(
      "addItem",
      function(event) {
        var stationName = event.detail.label;
        var stationCoords = stations[stationName];
        var longitude = stationCoords[0];
        var latitude = stationCoords[1];
        mapManager.addMarker(stationName, longitude, latitude);
      },
      false,
    )

    this.element.addEventListener(
      "removeItem",
      function(event) {
        var stationName = event.detail.label;
        mapManager.removeMarker(stationName);
      },
      false,
    )
  }
}