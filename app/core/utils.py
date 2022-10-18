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
            region = i['address_components'][0].get('long_name')
            if not region:
                data["region"] = None
            else:
                data["region"] = region

        if "administrative_area_level_2" in i['types']:
            province = i['address_components'][0].get('long_name')
            if not province:
                data["province"] = None
            else:
                data["province"] = province

        if "administrative_area_level_3" in i['types']:
            municipality = i['address_components'][0].get('long_name')
            if not municipality:
                data["municipality"] = None
            else:
                data["municipality"] = municipality

        if "neighborhood" in i['types'] or "administrative_area_level_5" in i['types']:
            barangay = i['address_components'][0].get('long_name')
            if not barangay:
                data["barangay"] = None
            else:
                data["barangay"] = barangay

    return data


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    return ip


if __name__ == "__main__":
    print(get_location(15.02, 120.16))
