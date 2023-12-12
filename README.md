# Notice of deprecation: 
Spike work for this project has now been complete. Find the production ready version of this project [here](https://github.com/ministryofjustice/juniper-mist-integration).

# Automated Juniper MIST integration 

This repo has been created as part of some spike work to automate the creation of Juniper Mist sites.

## Local Development:

Example of test data csv file. Create a file called this [test_data/sites_with_clients.csv](test_data/sites_with_clients.csv)
```
Client,Shared Secret,Site Name,Site Address,Enable GovWifi,Enable MoJWifi
192.168.1.2/32,0000000000000000000,"Site A", "Number 1 Foobar Road London UK", "TRUE", "FALSE"
192.168.1.3/32,0000000000000000000,"Site B", "Number 2 Foobar Road London UK", "TRUE", "FALSE"
192.168.1.4/32,0000000000000000000,"Site C", "Number 3 Foobar Road London UK", "TRUE", "FALSE"
```
Setup OS ENVs:

        google_api_key=os.environ['GOOGLE_API_KEY'],
        mist_api_token=os.environ['MIST_API_TOKEN'],
        org_id=os.environ['ORG_ID']

Setup Python Environment and install requirements.txt
