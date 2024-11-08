from enum import Enum

class LocationAttributes(Enum):
    id = 1
    name = 2
    link = 3
    location_address1 = 4
    location_city = 5
    location_state = 6
    location_stateAbbrev = 7
    location_postalCode = 8
    location_defaultCoordinates_latitude = 9
    location_defaultCoordinates_longitude = 10
    location_azimuthAngle = 11
    location_elevation = 12
    location_country = 13
    location_phone = 14
    timeZone_id = 15
    timeZone_offset = 16
    timeZone_offsetAtGameTime = 17
    timeZone_tz = 18
    fieldInfo_capacity = 19
    fieldInfo_turfType = 20
    fieldInfo_roofType = 21
    fieldInfo_leftLine = 22
    fieldInfo_left = 23
    fieldInfo_leftCenter = 24
    fieldInfo_center = 25
    fieldInfo_rightCenter = 26
    fieldInfo_right = 27
    fieldInfo_rightLine = 28
    active = 29
    season = 30

class TeamAttributes(Enum):
    all_star_status = 1
    id = 2
    name = 3
    link = 4
    season = 5
    venue_id = 6
    venue_name = 7
    venue_link = 8
    venue_active = 9
    venue_season = 10
    teamCode = 11
    fileCode = 12
    abbreviation = 13
    teamName = 14
    locationName = 15
    firstYearOfPlay = 16
    league_id = 17
    league_name = 18
    league_link = 19
    division_id = 20
    division_name = 21
    division_link = 22
    sport_id = 23
    sport_link = 24
    sport_name = 25
    shortName = 26
    parentOrgName = 27
    parentOrgId = 28
    franchiseName = 29
    clubName = 30
    active = 31