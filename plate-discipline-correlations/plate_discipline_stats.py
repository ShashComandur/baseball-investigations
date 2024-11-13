from enum import Enum

class Descriptors(Enum):
    NAME = "Name"
    SEASON = "Season"

class PlateDisciplineStats(Enum):
    O_SWING_PCT = "O-Swing%"
    O_CONTACT_PCT = "O-Contact%"
    Z_SWING_PCT = "Z-Swing%"
    Z_CONTACT_PCT = "Z-Contact%"
    SWING_PCT = "Swing%"
    CONTACT_PCT = "Contact%"
    ZONE_PCT = "Zone%"
    F_STRIKE_PCT = "F-Strike%"
    SW_STR_PCT = "SwStr%"

class Outcomes(Enum):
    BB_PCT = "BB%"
    WOBA = "wOBA"