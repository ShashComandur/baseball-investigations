from pybaseball import team_game_logs
from enums import MLBTeams, MLBParks
import pandas as pd


def main():
    # Create list of park nodes first
    park_nodes = []
    for park in MLBParks:
        team_name = get_team_from_park(
            park.value
        )  # Note: using park.value since it's an enum
        park_nodes.append(
            {
                "id": park.value,
                "name": park.value,
                "team": team_name,
                "home_venue": park.value,
            }
        )

    all_nodes = pd.DataFrame(park_nodes)
    all_edges = pd.DataFrame()

    for team in MLBTeams:
        data = team_game_logs(2024, team.value, "pitching")
        data["pitcher_list"] = [parse_pitchers(x) for x in data["PitchersUsed"]]

        team_nodes = create_nodes_list(data, team.value)
        team_edges = create_pitcher_park_edges(data, team.value)

        all_nodes = pd.concat([all_nodes, team_nodes], ignore_index=True)
        all_edges = pd.concat([all_edges, team_edges], ignore_index=True)

    all_nodes = all_nodes.drop_duplicates(subset=["id"])
    all_edges = all_edges.drop_duplicates(subset=["source", "destination"])

    # Add park nodes

    # Save combined files
    all_nodes.to_csv("gephi-tests/mlb_nodes_2024.csv", index=False)
    all_edges.to_csv("gephi-tests/mlb_edges_2024.csv", index=False)

    print(f"Total nodes: {len(all_nodes)}")
    print(f"Total edges: {len(all_edges)}")

    print(all_nodes)
    print(all_edges)


def create_nodes_list(data, team):
    """
    Create a DataFrame of nodes containing both pitchers and parks.

    Args:
        data (pandas.DataFrame): DataFrame containing 'pitcher_list' and park information

    Returns:
        pandas.DataFrame: Node list with columns 'id', 'name', 'team', 'home_venue'
    """
    # Create nodes list
    nodes = []

    # Get all unique pitchers
    all_pitchers = set()
    for pitchers in data["pitcher_list"]:
        all_pitchers.update(pitchers)

    # Add pitcher nodes
    for pitcher in all_pitchers:
        # Find the team for this pitcher
        for _, row in data.iterrows():
            if pitcher in row["pitcher_list"]:
                team_name = team
                nodes.append(
                    {
                        "id": pitcher,
                        "name": pitcher,
                        "team": team_name,
                        "home_venue": MLBParks[MLBTeams(team_name).name].value,
                    }
                )
                break

    # Convert to DataFrame
    node_df = pd.DataFrame(nodes)

    # Save to CSV
    node_df.to_csv("pitcher_park_nodes.csv", index=False)

    print(f"Extracted nodes for {team}")
    return node_df


def create_pitcher_park_edges(data, team):
    """
    Create a DataFrame of directed edges from pitchers to parks with weights
    based on number of appearances.

    Args:
        data (pandas.DataFrame): DataFrame containing 'pitcher_list' and park information

    Returns:
        pandas.DataFrame: Edge list with columns 'source', 'destination', and 'weight'
    """
    import pandas as pd
    from collections import defaultdict

    # Dictionary to store pitcher-park appearances
    appearances = defaultdict(int)

    # Iterate through each row
    for _, row in data.iterrows():
        park = (
            MLBParks[MLBTeams(team).name].value
            if row["Home"]
            else MLBParks[MLBTeams(row["Opp"]).name].value
        )
        pitchers = row["pitcher_list"]

        # Count each pitcher's appearance at this park
        for pitcher in pitchers:
            appearances[(pitcher, park)] += 1

    # Convert to DataFrame
    edges = []
    for (pitcher, park), count in appearances.items():
        edges.append({"source": pitcher, "destination": park, "weight": count})

    # Create DataFrame and sort by weight descending
    edge_df = pd.DataFrame(edges)
    edge_df = edge_df.sort_values("weight", ascending=False)

    # Save to CSV
    edge_df.to_csv("pitcher_park_edges.csv", index=False)

    print(f"Extracted edges for {team}")
    return edge_df


def get_all_pitchers(df):
    """
    Create a set of all unique pitchers used throughout the season.

    Args:
        df (pandas.DataFrame): DataFrame containing a 'PitchersUsed' column
                             with lists of pitcher names

    Returns:
        set: Set of all unique pitcher names used in the season
    """
    # Initialize empty set to store all pitchers
    all_pitchers = set()

    # Iterate through each row's pitcher list
    for pitchers_list in df["PitchersUsed"]:
        # Parse the pitchers string if it hasn't been parsed yet
        if isinstance(pitchers_list, str):
            pitchers_list = parse_pitchers(pitchers_list)

        # Add each pitcher to the set
        all_pitchers.update(pitchers_list)

    return all_pitchers


def get_team_from_park(park_name):
    """Get the team name from the park name using the MLBParks enum"""
    for team in MLBParks:
        if team.value == park_name:
            return team.name.replace("_", " ").title()
    return None


def get_home_park_from_team(team_name):
    """Get the home park from the team name using the MLBParks enum"""
    # Convert team name to enum format
    enum_name = team_name.upper().replace(" ", "_")
    try:
        return MLBParks[enum_name].value
    except KeyError:
        return None


def parse_pitchers(pitcher_string):
    """
    Parse a string of pitchers used into a list of pitcher names.

    Args:
        pitcher_string (str): String containing pitcher information in format like
                            "Z.Gallen (99-58-W), S.McGough (99), M.Castro (...)"

    Returns:
        list: List of pitcher names without the additional information
    """
    # Split the string by commas
    pitchers = pitcher_string.split(",")

    # Clean each pitcher name
    cleaned_pitchers = []
    for pitcher in pitchers:
        # Find the opening parenthesis and take everything before it
        paren_index = pitcher.find("(")
        if paren_index != -1:
            name = pitcher[:paren_index]
        else:
            name = pitcher

        # Clean up any remaining whitespace
        name = name.strip()
        if name:  # Only add non-empty names
            cleaned_pitchers.append(name)
    return cleaned_pitchers


if __name__ == "__main__":
    main()
