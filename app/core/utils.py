import googlemaps
import os


def get_location(lat, lon):
    gmaps = googlemaps.Client(key=os.environ.get('GMAPS_TOKEN'))
    data = {'lat': lat, 'lon': lon}
    reverse_geocode_result = gmaps.reverse_geocode(
        (data['lat'],
         data['lon']),
        result_type='political')

    if not reverse_geocode_result:
        return None
    for i in reverse_geocode_result:
        if "administrative_area_level_1" in i['types']:
            data["region"] = i['address_components'][0].get('long_name')
        if "administrative_area_level_2" in i['types']:
            data["province"] = i['address_components'][0].get('long_name')
        if "administrative_area_level_3" in i['types']:
            data["municipality"] = i['address_components'][0].get('long_name')
        if "administrative_area_level_5" in i['types']:
            data["barangay"] = i['address_components'][0].get('long_name')
    return data


if __name__ == "__main__":
    print(get_location(15.02, 120.16))
