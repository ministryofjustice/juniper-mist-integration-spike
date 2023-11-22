import sys, time, requests, csv, json

# Convert CSV file to JSON object.
def csv_to_json(file):
    csv_rows = []
    with open(file) as csvfile:
        reader = csv.DictReader(csvfile)
        title = reader.fieldnames

        for row in reader:
            csv_rows.extend([ {title[i]: row[title[i]] for i in range(len(title))} ])

    return csv_rows


# Google geocode the site address.
# Note: The Google Maps Web Services Client Libraries could also be used, rather than directly calling the REST APIs.
# Documentation: https://developers.google.com/maps/documentation/geocoding/client-library
def geocode(address, google_api_key, show_more_details):
    if address is None or address == '':
        return (False, 'Missing site address')

    try:
        # Establish Google session
        google = Google(google_api_key)

        # Call the Google Geocoding API: https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={google_api_key}
        # Documentation: https://developers.google.com/maps/documentation/geocoding/intro
        print('Calling the Google Geocoding API...')
        url = 'https://maps.googleapis.com/maps/api/geocode/json?address={}'.format(address.replace(' ', '+'))
        result = google.get(url)
        if result == False:
            return (False, 'Failed to get Geocoding')

        if show_more_details:
            print('\nRetrieving the JSON response object...')
            print(json.dumps(result, sort_keys=True, indent=4))

        gaddr = result['results'][0]
        if show_more_details:
            print('\nRetrieving the results[0] object...')
            print(json.dumps(gaddr, sort_keys=True, indent=4))

        location = gaddr['geometry']['location']
        if show_more_details:
            print('\nRetrieving the geometry.location object...')
            print(json.dumps(location, sort_keys=True, indent=4))
            print('\nUsing lat and lng in the Google Time Zone API request')

        print()

        # Call the Google Time Zone API: https://maps.googleapis.com/maps/api/timezone/json?location={lat},{lng}&timestamp={timestamp}&key={google_api_key}
        # Documentation: https://developers.google.com/maps/documentation/timezone/start
        print('Calling the Google Time Zone API...')
        url = 'https://maps.googleapis.com/maps/api/timezone/json?location={},{}&timestamp={}'.format(location['lat'], location['lng'], int(time.time()))
        result = google.get(url)
        if result == False:
            return (False, 'Failed to get Time Zone')

        gtz = result
        if show_more_details:
            print('\nRetrieving the JSON response object...')
            print(json.dumps(result, sort_keys=True, indent=4))

        print()
    except Exception as e:
        return (False, str(e))

    results = {
        'address':
            gaddr['formatted_address'],
        'latlng': {
            'lat': location['lat'],
            'lng': location['lng'],
        },
        'country_code': [ x['short_name'] for x in gaddr['address_components'] if 'country' in x['types'] ][0],
        'timezone':
            gtz['timeZoneId']
    }

    return (True, results)


# Google CRUD operations
class Google(object):
    def __init__(self, key=''):
        self.session = requests.Session()
        self.key = key

    def get(self, url):
        url += '&key={}'.format(self.key)
        session = self.session

        print('GET {}'.format(url))
        response = session.get(url)

        if response.status_code != 200:
            print('Failed to GET')
            print('\tURL: {}'.format(url))
            print('\tResponse: {} ({})'.format(response.text, response.status_code))

            return False

        return json.loads(response.text)


# Mist CRUD operations
class Admin(object):
    def __init__(self, token=''):
        self.session = requests.Session()
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Token ' + token
        }

    def post(self, url, payload, timeout=60):
        url = 'https://api.eu.mist.com{}'.format(url)
        session = self.session
        headers = self.headers

        print('POST {}'.format(url))
        response = session.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            print('Failed to POST')
            print('\tURL: {}'.format(url))
            print('\tPayload: {}'.format(payload))
            print('\tResponse: {} ({})'.format(response.text, response.status_code))

            return False

        return json.loads(response.text)

    def put(self, url, payload):
        url = 'https://api.eu.mist.com{}'.format(url)
        session = self.session
        headers = self.headers

        print('PUT {}'.format(url))
        response = session.put(url, headers=headers, json=payload)

        if response.status_code != 200:
            print('Failed to PUT')
            print('\tURL: {}'.format(url))
            print('\tPayload: {}'.format(payload))
            print('\tResponse: {} ({})'.format(response.text, response.status_code))

            return False

        return json.loads(response.text)


# Main function
def juniper_script(file,
         google_api_key='',
         mist_api_token='',
         org_id=''):

    # file = 'sites.csv'
    # google_api_key = ''  # Your Google API key goes here. Documentation: https://cloud.google.com/docs/authentication/api-keys
    # mist_api_token = ''  # Your Mist API token goes here. Documentation: https://api.mist.com/api/v1/docs/Auth#api-token
    # org_id = ''  # Your Organization ID goes here

    show_more_details = True  # Configure True/False to enable/disable additional logging of the API response objects


    # Check for required variables
    # if google_api_key == '':
    #     print('Please provide your Google API key as google_api_key')
    #     sys.exit(1)
    if mist_api_token == '':
        print('Please provide your Mist API token as mist_api_token')
        sys.exit(1)
    elif org_id == '':
        print('Please provide your Mist Organization UUID as org_id')
        sys.exit(1)

    # Establish Mist session
    admin = Admin(mist_api_token)

    # Convert CSV to valid JSON
    data = csv_to_json(file)
    if data == None or data == []:
        print('Failed to convert CSV file to JSON. Exiting script.')
        sys.exit(2)

    # Create each site from the CSV file
    for d in data:
        # Variables
        site_id = None
        site = {'name': d.get('Site Name', ''),
                'address': d.get('Site Name', ''),
                #TODO this would need to come from a geocoding source: latlng, country_code, timezone
                "latlng": { "lat": 37.295833, "lng": -122.032946 },
                "country_code": "GB",
                "timezone": "Europe/London",
                }

        # Provide your Site Setting.
        # Example can be found here: https://api.mist.com/api/v1/docs/Site#site-setting
        '''
        ie:
        {
          'rtsa': { 'enabled': True },			    # Enable vBLE Engagement
          'auto_upgrade': { 'enabled': False },	# Disable Auto Upgrade
          'rogue': {
            'honeypot_enabled': True		      	# Enable Honeypot APs
            'enabled': True,					          # Enable Rogue and Neighbor APs
            'min_rssi': -80,					          # Minimum Neighbor RSSI Threshold -80
          }
        }
        '''
        # MOJ specific attributes
        site_setting = {

            "vars": {
                "Enable GovWifi": d.get('Enable GovWifi', ''), #Not exported from NACS
                "Enable MoJWifi": d.get('Enable MoJWifi', ''), #Not exported from NACS
                "Weird NACS Radius Key": d.get('Shared Secret', ''),
                "GovWifi Radius Key": "WHERE DO I GET THIS?"

            }

        }

        # # Create Site
        # (geocoded, geocoding) = geocode(d.get('Site Address', ''), google_api_key, show_more_details)
        # if geocoded == True:
        #     site.update(geocoding)
        # else:
        #     print('Failed to geocode...')
        #     print(geocoding)
        #     print()
    #
        print('Calling the Mist Create Site API...')
        result = admin.post('/api/v1/orgs/' + org_id + '/sites', site)
        if result == False:
            print('Failed to create site {}'.format(site['name']))
            print('Skipping remaining operations for this site...')
            print('\n\n==========\n\n')

            continue
        else:
            site_id = result['id']
            print('Created site {} ({})'.format(site['name'], site_id))

            if show_more_details:
                print('\nRetrieving the JSON response object...')
                print(json.dumps(result, sort_keys=True, indent=4))
                print('\nUsing id in the Mist Update Setting API request')

        print()

        # Update Site Setting
        print('Calling the Mist Update Setting API...')
        result = admin.put('/api/v1/sites/' + site_id + '/setting',
                           site_setting)
        if result == False:
            print('Failed to update site setting {} ({})'.format(site['name'], site_id))
        else:
            print('Updated site setting {} ({})'.format(site['name'], site_id))

            if show_more_details:
                print('\nRetrieving the JSON response object...')
                print(json.dumps(result, sort_keys=True, indent=4))

        print('\n\n==========\n\n')
