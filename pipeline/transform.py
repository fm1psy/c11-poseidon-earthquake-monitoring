example = [{'type': 'Feature',
            'properties': {'mag': 0.67,
                           'place': '13 km WSW of Searles Valley, CA',
                           'time': 1718718656830,
                           'updated': 1718720255694,
                           'tz': None,
                           'url': 'https://earthquake.usgs.gov/earthquakes/eventpage/ci40801680',
                           'detail': 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/detail/ci40801680.geojson',
                           'felt': None,
                           'cdi': None,
                           'mmi': None,
                           'alert': None,
                           'status': 'reviewed',
                           'tsunami': 0,
                           'sig': 7,
                           'net': 'ci',
                           'code': '40801680',
                           'ids': ',ci40801680,',
                           'sources': ',ci,',
                           'types': ',nearby-cities,origin,phase-data,scitech-link,',
                           'nst': 17,
                           'dmin': 0.1163,
                           'rms': 0.13,
                           'gap': 146,
                           'magType': 'ml',
                           'type': 'earthquake',
                           'title': 'M 0.7 - 13 km WSW of Searles Valley, CA'},
            'geometry': {'type': 'Point', 'coordinates': [-117.542, 35.7305, 1.88]},
            'id': 'ci40801680'}]


def get_earthquake_property(data, property):
    return data['properties'][property]


def get_earthquake_geometry(data, geometry):
    return data['geometry'][geometry]


def get_earthquake_id(data):
    return data['id']


def get_earthquake_data(data):
    status = get_earthquake_property(data, 'status')
    network = get_earthquake_property(data, 'net')
    magtype = get_earthquake_property(data,'magType')
    type = get_earthquake_property(data, 'type')
    magnitude = get_earthquake_property(data, 'mag')
    lon = get_earthquake_geometry(data, 'coordinates')[0]
    lat = get_earthquake_geometry(data, 'coordinates')[1]
    depth = get_earthquake_geometry(data, 'coordinates')[2]
    time = get_earthquake_property(data, 'time')
    felt = get_earthquake_property(data, 'felt')
    cdi = get_earthquake_property(data, 'cdi')
    mmi = get_earthquake_property(data, 'mmi')
    significance = get_earthquake_property(data, 'sig')
    nst = get_earthquake_property(data,'nst')
    dmin = get_earthquake_property(data, 'dmin')
    gap = get_earthquake_property(data, 'gap')
    title = get_earthquake_property(data, 'title')

    return {
        'status': status,
        'network': network,
        'magtype': magtype,
        'type': type,
        'magnitude': magnitude,
        'longitude': lon,
        'latitude': lat,
        'depth': depth,
        'time': time,
        'felt': felt,
        'cdi': cdi,
        'mmi': mmi,
        'significance': significance,
        'nst': nst,
        'dmin': dmin,
        'gap': gap,
        'title': title
    }




if __name__ == "__main__":
    for data in example:
        print(get_earthquake_data(data))

