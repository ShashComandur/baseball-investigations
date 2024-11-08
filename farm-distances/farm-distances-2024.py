import json
import os
import psycopg2
import requests
import traceback

from dotenv import load_dotenv
from flatten_json import flatten
from enums import LocationAttributes, TeamAttributes

def main():
    load_dotenv()
    get_data_from_mlb_api()
    store_data_in_postgres()

"""
Get team and stadium location data from MLB's API.
"""
def get_data_from_mlb_api():   
    base_url='https://statsapi.mlb.com/api/v1/'

    # hit `mlb-stats/api/v1/teams` to get team data from 2024 active teams
    data = { "season": 2024, "activeStatus": "Y", "hydrate": "venue" }
    teams = requests.get(url=base_url + 'teams/', params=data).json()['teams']

    # extract venue info for each team
    venues = [team['venue'] if 'venue' in team else None for team in teams]
    
    # hit `mlb-stats/api/v1/venue/{venueIds}` to get location data for each venue
    # (wish i could get this in the first call, but not an option per API documentation)
    locations = []
    for venue in venues:
        data = { "venueIds": venue["id"], "hydrate": "timezone,fieldInfo,location,relatedVenues" }
        locations.append(requests.get(url=base_url + 'venues/', params=data).json())

    # saving to json instead of passing the data on, as there are too many records
    with open('teams.json', 'w') as outfile:
        json.dump(teams, outfile, indent=4)
    with open('locations.json', 'w') as outfile:
        json.dump(locations, outfile, indent=4)

"""
Store the API results in a PostgreSQL DB.
"""
def store_data_in_postgres():
    # get data from JSON files
    with open('teams.json', 'r') as f:
        raw_teams = json.load(f)
    with open('locations.json', 'r') as f:
        raw_locations = json.load(f)

    flattened_teams = [flatten(team) for raw_team in raw_teams]
    flattened_locations = [flatten(venue) for raw_location in raw_locations for venue in raw_location["venues"]]

    filtered_teams = remove_duplicates_by_id(flattened_teams)
    filtered_locations = remove_duplicates_by_id(flattened_locations)
   
    # connect to DB
    try:
        connection = psycopg2.connect(
            user=os.getenv('PG_USERNAME'),
            password=os.getenv('PG_PASSWORD'),
            host=os.getenv('PG_HOST'),
            port=os.getenv('PG_PORT'),
            database=os.getenv('PG_DATABASE')
        )
        cursor = connection.cursor()

        print("PostgreSQL Connection Diagnostic Information")
        print(connection.get_dsn_parameters(), "\n")
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print(f"Connected to - {record}!\n")

        # create the two tables if they do not exist
        create_teams_table = """
        CREATE TABLE IF NOT EXISTS teams (
            all_star_status BOOLEAN,
            id INTEGER PRIMARY KEY,
            name VARCHAR(255),
            link VARCHAR(255),
            season INTEGER,
            venue_id INTEGER,
            venue_name VARCHAR(255),
            venue_link VARCHAR(255),
            venue_active BOOLEAN,
            venue_season VARCHAR(255),
            teamCode VARCHAR(255),
            fileCode VARCHAR(255),
            abbreviation VARCHAR(255),
            teamName VARCHAR(255),
            locationName VARCHAR(255),
            firstYearOfPlay VARCHAR(255),
            league_id INTEGER,
            league_name VARCHAR(255),
            league_link VARCHAR(255),
            division_id INTEGER,
            division_name VARCHAR(255),
            division_link VARCHAR(255),
            sport_id INTEGER,
            sport_link VARCHAR(255),
            sport_name VARCHAR(255),
            shortName VARCHAR(255),
            parentOrgName VARCHAR(255),
            parentOrgId INTEGER,
            franchiseName VARCHAR(255),
            clubName VARCHAR(255),
            active BOOLEAN
        );
        """
        cursor.execute(create_teams_table)
    
        create_locations_table = """
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY,
            name VARCHAR(255),
            link VARCHAR(255),
            location_address1 VARCHAR(255),
            location_city VARCHAR(255),
            location_state VARCHAR(255),
            location_stateAbbrev VARCHAR(255),
            location_postalCode VARCHAR(255),
            location_defaultCoordinates_latitude FLOAT(20),
            location_defaultCoordinates_longitude FLOAT(20),
            location_azimuthAngle FLOAT(20),
            location_elevation INTEGER,
            location_country VARCHAR(255),
            location_phone VARCHAR(255),
            timeZone_id VARCHAR(255),
            timeZone_offset INTEGER,
            timeZone_offsetAtGameTime INTEGER,
            timeZone_tz VARCHAR(255),
            fieldInfo_capacity INTEGER,
            fieldInfo_turfType VARCHAR(255),
            fieldInfo_roofType VARCHAR(255),
            fieldInfo_leftLine INTEGER,
            fieldInfo_left INTEGER,
            fieldInfo_leftCenter INTEGER,
            fieldInfo_center INTEGER,
            fieldInfo_rightCenter INTEGER,
            fieldInfo_right INTEGER,
            fieldInfo_rightLine INTEGER,
            active BOOLEAN,
            season VARCHAR(255)
        );
        """
        cursor.execute(create_locations_table)
        connection.commit() 
       
        # insert rows from flattened and filtered data
        for team in filtered_teams:
            to_insert = format_insert_as_tuple(team, TeamAttributes)
            query = f"""
            INSERT INTO teams (
                all_star_status, id, name, link, season, venue_id, venue_name, venue_link, venue_active, venue_season, teamCode, fileCode, abbreviation, teamName, locationName, firstYearOfPlay, league_id, league_name, league_link, division_id, division_name, division_link, sport_id, sport_link, sport_name, shortName, parentOrgName, parentOrgId, franchiseName, clubName, active
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, to_insert)
            connection.commit() 

        for location in filtered_locations:
            to_insert = format_insert_as_tuple(location, LocationAttributes)
            query = f"""
            INSERT INTO locations (
                id, name, link, location_address1, location_city, location_state, location_stateAbbrev, location_postalCode, location_defaultCoordinates_latitude, location_defaultCoordinates_longitude, location_azimuthAngle, location_elevation, location_country, location_phone, timeZone_id, timeZone_offset, timeZone_offsetAtGameTime, timeZone_tz, fieldInfo_capacity, fieldInfo_turfType, fieldInfo_roofType, fieldInfo_leftLine, fieldInfo_left, fieldInfo_leftCenter, fieldInfo_center, fieldInfo_rightCenter, fieldInfo_right, fieldInfo_rightLine, active, season
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, to_insert)
            connection.commit()

    except Exception:
        traceback.print_exc()
    finally:
        if (connection):
            cursor.close()
            connection.close()
            print("Closing connection....")

"""
Helper method to format and insert tuple.
Using an enum here so that we can capture null values, since not every attribute is present for every row.
"""
def format_insert_as_tuple(dict, attributes_enum):
    to_insert = []
    for attribute in (attributes_enum):
        to_insert.append(dict.get(attribute.name, None))
    to_insert = tuple(to_insert)
    return to_insert

"""
Helper method to prune duplicate records from raw data.
"""
def remove_duplicates_by_id(list_of_dicts):
    seen_ids = set()
    unique_dicts = []
    for dictionary in list_of_dicts:
        if dictionary['id'] not in seen_ids:
            unique_dicts.append(dictionary)
            seen_ids.add(dictionary['id'])
    return unique_dicts

if __name__ == "__main__":
    main()