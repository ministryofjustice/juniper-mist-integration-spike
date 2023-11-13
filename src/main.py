from juniper import juniper_script
import os




if __name__ == '__main__':

    #def geocoding():
        # Call opensource API, input site address
        # OUTPUT latlng, country_code, timezone

    juniper_script(
        file=os.getcwd() + '/../test_data/sites_with_clients.csv',
        #google_api_key=os.environ['GOOGLE_API_KEY'],
        mist_api_token=os.environ['MIST_API_TOKEN'],
        org_id=os.environ['ORG_ID']
    )
